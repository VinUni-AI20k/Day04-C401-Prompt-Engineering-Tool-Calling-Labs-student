from __future__ import annotations

import unittest

from tools.source_check.tool import check_sources


class SourceCheckTest(unittest.TestCase):
    def test_check_sources_flags_duplicates_and_counts_domains(self) -> None:
        result = check_sources(
            items=[
                {"title": "OpenAI update", "url": "https://openai.com/research/", "source": "OpenAI"},
                {"title": "Duplicate", "url": "https://openai.com/research", "source": "OpenAI"},
                {"title": "HTTP page", "url": "http://example.com/post", "source": ""},
            ],
            min_sources=2,
        )

        self.assertEqual(result["tool"], "source_check")
        self.assertEqual(result["item_count"], 3)
        self.assertEqual(result["valid_url_count"], 3)
        self.assertEqual(result["unique_domain_count"], 2)
        self.assertEqual(result["duplicate_urls"], ["https://openai.com/research"])
        self.assertIn("duplicate_url", result["items"][1]["checks"])
        self.assertIn("insecure_http", result["items"][2]["checks"])
        self.assertIn("missing_source", result["items"][2]["checks"])
        self.assertEqual(result["recommendation"], "ok")

    def test_check_sources_recommends_more_sources_when_domain_diversity_is_low(self) -> None:
        result = check_sources(
            items=[
                {"title": "Only source", "url": "https://openai.com/news/a", "source": "OpenAI"},
                {"title": "Same source", "url": "https://openai.com/news/b", "source": "OpenAI"},
            ],
            min_sources=2,
        )

        self.assertEqual(result["unique_domain_count"], 1)
        self.assertEqual(result["recommendation"], "needs_more_independent_sources")


if __name__ == "__main__":
    unittest.main()
