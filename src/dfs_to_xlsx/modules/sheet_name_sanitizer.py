# SPDX-License-Identifier: MIT

from __future__ import annotations  # Future-proof type annotations


class SheetNameSanitizer:
    """Sanitize Excel sheet names to comply with Excel's naming rules.

    Excel enforces restrictions on worksheet names, including:
        - Maximum length of 31 characters
        - Disallowed characters: : \ / ? * [ ]
        - No leading/trailing apostrophes
        - Must be unique within a workbook

    This class provides a reusable sanitization method that ensures any
    provided sheet name is transformed into a valid, safe, and unique name.
    """

    INVALID_CHARS = set(r":\/?*[]")
    MAX_LEN = 31

    def sanitize(self, name: str, existing: set[str]) -> str:
        """Return a sanitized, valid, and unique Excel sheet name.

        Args:
            name (str): Original sheet name.
            existing (set[str]): Already-used sheet names.

        Returns:
            str: Sanitized and unique sheet name.

        """
        # Remove invalid characters
        cleaned = "".join(ch for ch in name if ch not in self.INVALID_CHARS).strip()

        # Trim to Excel max length
        cleaned = cleaned[: self.MAX_LEN]

        # Remove leading/trailing apostrophes
        cleaned = cleaned.strip("'")

        # Fallback if empty
        if not cleaned:
            cleaned = "Sheet"

        # Ensure uniqueness
        base = cleaned
        counter = 1

        while cleaned in existing:
            suffix = f"_{counter}"
            cleaned = base[: self.MAX_LEN - len(suffix)] + suffix
            counter += 1

        return cleaned
