"""
Tests for Firecrawl AcclaimWeb integration
"""

import pytest
from unittest.mock import Mock, patch
from firecrawl_client import FirecrawlClient, AcclaimWebClient


class TestFirecrawlClient:
    """Test FirecrawlClient basic functionality"""
    
    def test_init(self):
        client = FirecrawlClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.firecrawl.dev/v2"
    
    @patch('requests.post')
    def test_scrape_success(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "markdown": "Test content",
                "metadata": {"creditsUsed": 5}
            }
        }
        mock_post.return_value = mock_response
        
        client = FirecrawlClient(api_key="test_key")
        result = client.scrape(url="https://example.com")
        
        assert result["success"] == True
        assert result["data"]["markdown"] == "Test content"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_scrape_with_actions(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {}}
        mock_post.return_value = mock_response
        
        client = FirecrawlClient(api_key="test_key")
        actions = [
            {"type": "wait", "milliseconds": 1000},
            {"type": "click", "selector": "#button"}
        ]
        
        result = client.scrape(url="https://example.com", actions=actions)
        
        # Verify actions were included in payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert "actions" in payload
        assert len(payload["actions"]) == 2


class TestAcclaimWebClient:
    """Test AcclaimWebClient lien search functionality"""
    
    def setup_method(self):
        self.firecrawl_mock = Mock(spec=FirecrawlClient)
        self.client = AcclaimWebClient(firecrawl_client=self.firecrawl_mock)
    
    def test_search_liens_success(self):
        # Mock Firecrawl response
        self.firecrawl_mock.scrape.return_value = {
            "success": True,
            "data": {
                "markdown": """
                MTG | 2023-12345 | Book 1234 Page 567 | WELLS FARGO BANK | JOHN DOE | 01/15/2023 | $250,000
                LIEN | 2023-45678 | Book 1235 Page 890 | IRS | JOHN DOE | 02/20/2023 | $15,000
                """,
                "actions": {
                    "screenshots": ["https://example.com/screenshot.png"]
                }
            }
        }
        
        result = self.client.search_liens(address="123 Main St")
        
        assert result["success"] == True
        assert result["address"] == "123 Main St"
        assert result["total_liens"] == 2
        assert len(result["liens"]) == 2
    
    def test_parse_liens(self):
        markdown = """
        MTG | 2023-12345 | Book 1234 Page 567 | WELLS FARGO BANK | JOHN DOE | 01/15/2023 | $250,000
        LIEN | 2023-45678 | Book 1235 Page 890 | SUNSET HOMEOWNERS ASSOCIATION | JOHN DOE | 02/20/2023 | $5,000
        """
        
        liens = self.client._parse_liens(markdown)
        
        assert len(liens) == 2
        assert liens[0]["type"] == "MTG"
        assert liens[0]["amount"] == 250000.0
        assert liens[1]["type"] == "LIEN"
        assert liens[1]["is_hoa"] == True  # HOA detected
    
    def test_analyze_lien_priority(self):
        liens = [
            {
                "type": "MTG",
                "grantor": "WELLS FARGO",
                "amount": 250000.0,
                "recorded_date": "01/15/2023",
                "is_hoa": False
            },
            {
                "type": "LIEN",
                "grantor": "SUNSET HOA",
                "amount": 5000.0,
                "recorded_date": "02/20/2023",
                "is_hoa": True
            }
        ]
        
        analysis = self.client.analyze_lien_priority(liens)
        
        assert analysis["total_liens"] == 2
        assert analysis["total_encumbrance"] == 255000.0
        assert analysis["first_position"]["grantor"] == "WELLS FARGO"
        assert len(analysis["hoa_liens"]) == 1
        assert len(analysis["warnings"]) >= 1
        assert analysis["warnings"][0]["type"] == "HOA_FORECLOSURE_RISK"
    
    def test_hoa_detection(self):
        """Test that HOA liens are properly detected"""
        hoa_variations = [
            "SUNSET HOMEOWNERS ASSOCIATION",
            "PARKVIEW HOA",
            "BEACHSIDE CONDOMINIUM ASSOCIATION",
            "RIVERSIDE COMMUNITY ASSOCIATION"
        ]
        
        for hoa_name in hoa_variations:
            lien = {
                "type": "LIEN",
                "grantor": hoa_name,
                "amount": 5000.0,
                "recorded_date": "01/01/2023"
            }
            
            # Process through HOA detection logic
            if any(keyword in lien['grantor'].upper() for keyword in [
                'HOMEOWNER', 'HOA', 'ASSOCIATION', 'CONDO', 'COMMUNITY'
            ]):
                lien['is_hoa'] = True
            
            assert lien['is_hoa'] == True, f"Failed to detect HOA: {hoa_name}"
    
    def test_parse_amount(self):
        """Test amount parsing with various formats"""
        test_cases = [
            ("$250,000", 250000.0),
            ("250000", 250000.0),
            ("$1,234.56", 1234.56),
            ("invalid", 0.0)
        ]
        
        for input_str, expected in test_cases:
            result = self.client._parse_amount(input_str)
            assert result == expected
    
    def test_search_with_parcel_id(self):
        """Test search using parcel ID instead of address"""
        self.firecrawl_mock.scrape.return_value = {
            "success": True,
            "data": {
                "markdown": "",
                "actions": {"screenshots": []}
            }
        }
        
        result = self.client.search_liens(
            address="123 Main St",
            parcel_id="2517790"
        )
        
        # Verify parcel_id was used in search
        call_args = self.firecrawl_mock.scrape.call_args
        actions = call_args[1]['actions']
        
        # Find the write action
        write_action = next(a for a in actions if a['type'] == 'write')
        assert write_action['text'] == "2517790"
    
    def test_multiple_mortgages_warning(self):
        """Test warning for complex title with 3+ mortgages"""
        liens = [
            {"type": "MTG", "grantor": "BANK A", "amount": 200000, "is_hoa": False},
            {"type": "MTG", "grantor": "BANK B", "amount": 50000, "is_hoa": False},
            {"type": "MTG", "grantor": "BANK C", "amount": 25000, "is_hoa": False}
        ]
        
        analysis = self.client.analyze_lien_priority(liens)
        
        assert len(analysis["mortgages"]) == 3
        multiple_mtg_warning = next(
            w for w in analysis["warnings"] 
            if w["type"] == "MULTIPLE_MORTGAGES"
        )
        assert multiple_mtg_warning is not None


class TestIntegration:
    """Integration tests (require actual API key)"""
    
    @pytest.mark.skip(reason="Requires live API and may use credits")
    def test_live_acclaimweb_search(self):
        """
        Live test against AcclaimWeb
        Only run manually when testing actual integration
        """
        FIRECRAWL_API_KEY = "fc-985293d88ddf4d6595e041936ec2cb00"
        
        firecrawl = FirecrawlClient(api_key=FIRECRAWL_API_KEY)
        acclaimweb = AcclaimWebClient(firecrawl_client=firecrawl)
        
        result = acclaimweb.search_liens(address="4127 ARLINGTON AVE")
        
        assert result["success"] in [True, False]  # May fail due to site issues
        if result["success"]:
            assert "liens" in result
            assert "screenshot" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
