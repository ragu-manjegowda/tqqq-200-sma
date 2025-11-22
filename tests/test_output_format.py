"""
Tests for output format compatibility with GitHub Actions workflow.

This ensures the main script output can be properly parsed by the
daily-signal.yml GitHub Actions workflow.
"""
import pytest
import subprocess
import re
from io import StringIO


class TestOutputFormat:
    """Test that script output matches expected format for GitHub Actions."""

    def test_script_runs_successfully(self):
        """Test that the main script can be executed."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Script should complete (exit code 0 or 1 is ok)
        assert result.returncode in [0, 1], f"Script failed with exit code {result.returncode}"

        # Should produce output
        assert len(result.stdout) > 0, "Script produced no output"

    def test_required_fields_present(self):
        """Test that all required fields are present in output."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Required fields for GitHub Actions parsing
        required_patterns = [
            r'Date:\s+\d{4}-\d{2}-\d{2}',              # Date: 2025-11-22
            r'QQQ Close:\s+\$[\d,]+\.\d{2}',           # QQQ Close: $585.67
            r'TQQQ Close:\s+\$[\d,]+\.\d{2}',          # TQQQ Close: $52.30
            r'SMA200:\s+\$[\d,]+\.\d{2}',              # SMA200: $542.35
            r'QQQ vs SMA200:\s+[+-]?\d+\.\d{2}%',      # QQQ vs SMA200: +7.99%
            r'BUY Threshold \(\+5%\):\s+\$[\d,]+\.\d{2}',   # BUY Threshold (+5%): $569.46
            r'SELL Threshold \(-3%\):\s+\$[\d,]+\.\d{2}',   # SELL Threshold (-3%): $526.08
            r'Position:\s+(CASH|TQQQ)',                # Position: TQQQ
        ]

        for pattern in required_patterns:
            assert re.search(pattern, output), f"Required pattern not found: {pattern}"

    def test_signal_status_present(self):
        """Test that a signal status is present in output."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # At least one of these status messages should be present
        status_patterns = [
            r'🟢 ALERT: BUY TQQQ',
            r'🔴 ALERT: SELL TQQQ',
            r'✅ STATUS: Holding TQQQ',
            r'⚪ STATUS: Holding CASH',
        ]

        found = any(re.search(pattern, output) for pattern in status_patterns)
        assert found, "No signal status found in output"

    def test_parseable_date_format(self):
        """Test that date format can be parsed."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Extract date
        date_match = re.search(r'Date:\s+(\d{4}-\d{2}-\d{2})', output)
        assert date_match, "Date not found in output"

        # Verify format
        date_str = date_match.group(1)
        assert len(date_str) == 10, f"Date format incorrect: {date_str}"
        assert date_str.count('-') == 2, f"Date format incorrect: {date_str}"

    def test_parseable_prices(self):
        """Test that prices can be extracted and are valid numbers."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Extract QQQ close price
        qqq_match = re.search(r'QQQ Close:\s+\$([\d,]+\.\d{2})', output)
        assert qqq_match, "QQQ Close not found"

        qqq_price_str = qqq_match.group(1).replace(',', '')
        qqq_price = float(qqq_price_str)
        assert qqq_price > 0, f"Invalid QQQ price: {qqq_price}"
        assert qqq_price < 10000, f"Unrealistic QQQ price: {qqq_price}"

        # Extract TQQQ close price
        tqqq_match = re.search(r'TQQQ Close:\s+\$([\d,]+\.\d{2})', output)
        assert tqqq_match, "TQQQ Close not found"

        tqqq_price_str = tqqq_match.group(1).replace(',', '')
        tqqq_price = float(tqqq_price_str)
        assert tqqq_price > 0, f"Invalid TQQQ price: {tqqq_price}"
        assert tqqq_price < 10000, f"Unrealistic TQQQ price: {tqqq_price}"

        # Extract SMA200
        sma_match = re.search(r'SMA200:\s+\$([\d,]+\.\d{2})', output)
        assert sma_match, "SMA200 not found"

        sma_price_str = sma_match.group(1).replace(',', '')
        sma_price = float(sma_price_str)
        assert sma_price > 0, f"Invalid SMA price: {sma_price}"

    def test_parseable_percentages(self):
        """Test that percentages can be extracted."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Extract QQQ vs SMA percentage
        pct_match = re.search(r'QQQ vs SMA200:\s+([+-]?\d+\.\d{2})%', output)
        assert pct_match, "QQQ vs SMA200 percentage not found"

        pct_value = float(pct_match.group(1))
        assert -100 < pct_value < 1000, f"Unrealistic percentage: {pct_value}%"

    def test_position_is_valid(self):
        """Test that position is either CASH or TQQQ."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Extract position
        position_match = re.search(r'Position:\s+(CASH|TQQQ)', output)
        assert position_match, "Position not found in output"

        position = position_match.group(1)
        assert position in ['CASH', 'TQQQ'], f"Invalid position: {position}"

    def test_github_actions_parsing_simulation(self):
        """Simulate the exact parsing logic used in GitHub Actions workflow."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Simulate the EXACT workflow parsing logic using awk-style field extraction
        def extract_field(pattern, field_num):
            """Extract specific field from line matching pattern (simulates grep | awk)."""
            for line in output.split('\n'):
                if re.search(pattern, line):
                    fields = line.split()
                    if len(fields) >= field_num:
                        return fields[field_num - 1]  # awk uses 1-based indexing
            return None

        # Extract using workflow patterns (matching .github/workflows/daily-signal.yml)
        signal = None
        for line in output.split('\n'):
            if re.search(r'(ALERT: BUY|ALERT: SELL|STATUS: Holding)', line):
                signal = line.strip()

        date = extract_field(r'Date:', 2)  # awk '{print $2}'
        qqq_close = extract_field(r'QQQ Close:', 3)  # awk '{print $3}'
        tqqq_close = extract_field(r'TQQQ Close:', 3)  # awk '{print $3}'
        sma200 = extract_field(r'SMA200:', 2)  # awk '{print $2}' (for line without "vs")
        qqq_vs_sma = extract_field(r'QQQ vs SMA200:', 4)  # awk '{print $4}'
        buy_threshold = extract_field(r'BUY Threshold', 4)  # awk '{print $4}'
        sell_threshold = extract_field(r'SELL Threshold', 4)  # awk '{print $4}'
        position = extract_field(r'Position:', 2)  # awk '{print $2}'

        # All fields should be extracted successfully
        assert signal is not None, "Failed to extract signal"
        assert date is not None, "Failed to extract date"
        assert qqq_close is not None, "Failed to extract QQQ close"
        assert tqqq_close is not None, "Failed to extract TQQQ close"
        assert sma200 is not None, "Failed to extract SMA200"
        assert qqq_vs_sma is not None, "Failed to extract QQQ vs SMA"
        assert buy_threshold is not None, "Failed to extract buy threshold"
        assert sell_threshold is not None, "Failed to extract sell threshold"
        assert position is not None, "Failed to extract position"

        # Verify we extracted ONLY VALUES, not labels
        assert not date.endswith(':'), f"Date should be just value, got: {date}"
        assert date.count('-') == 2, f"Date should be YYYY-MM-DD format, got: {date}"

        assert qqq_close.startswith('$'), f"QQQ close should start with $, got: {qqq_close}"
        assert not qqq_close.startswith('QQQ'), f"QQQ close should be just value, got: {qqq_close}"

        assert tqqq_close.startswith('$'), f"TQQQ close should start with $, got: {tqqq_close}"
        assert not tqqq_close.startswith('TQQQ'), f"TQQQ close should be just value, got: {tqqq_close}"

        assert sma200.startswith('$'), f"SMA200 should start with $, got: {sma200}"

        assert '%' in qqq_vs_sma, f"QQQ vs SMA should have %, got: {qqq_vs_sma}"
        assert not qqq_vs_sma.startswith('QQQ'), f"QQQ vs SMA should be just value, got: {qqq_vs_sma}"

        assert buy_threshold.startswith('$'), f"Buy threshold should start with $, got: {buy_threshold}"
        assert sell_threshold.startswith('$'), f"Sell threshold should start with $, got: {sell_threshold}"

        assert position in ['CASH', 'TQQQ'], f"Position should be CASH or TQQQ, got: {position}"

        # Verify values can be parsed as expected types
        # Date should be parseable
        from datetime import datetime
        datetime.strptime(date, '%Y-%m-%d')

        # Prices should be parseable (remove $ and ,)
        float(qqq_close.replace('$', '').replace(',', ''))
        float(tqqq_close.replace('$', '').replace(',', ''))
        float(sma200.replace('$', '').replace(',', ''))
        float(buy_threshold.replace('$', '').replace(',', ''))
        float(sell_threshold.replace('$', '').replace(',', ''))

        # Percentage should be parseable
        float(qqq_vs_sma.replace('%', '').replace('+', ''))


class TestWorkflowCompatibility:
    """Test specific GitHub Actions workflow compatibility."""

    def test_output_does_not_require_last_signal_date(self):
        """Test that 'Last Signal Date' line doesn't break parsing."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # There might be two Date: lines (Date and Last Signal Date)
        # Make sure we can distinguish them
        date_lines = [line for line in output.split('\n') if 'Date:' in line]

        # Should have at least one Date line
        assert len(date_lines) >= 1, "No Date line found"

        # The first one should be the market date (not Last Signal Date)
        first_date = date_lines[0]
        assert 'Last Signal' not in first_date, "First Date line is 'Last Signal Date'"

    def test_sma200_line_unique(self):
        """Test that SMA200 line can be uniquely identified."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Find all lines with SMA200
        sma_lines = [line for line in output.split('\n') if 'SMA200' in line]

        # Should have at least one
        assert len(sma_lines) >= 1, "No SMA200 line found"

        # The one without "vs" should be the plain SMA200 value
        plain_sma = [line for line in sma_lines if ' vs ' not in line]
        assert len(plain_sma) >= 1, "No plain SMA200 line found"

    def test_no_ambiguous_status_lines(self):
        """Test that status lines are unambiguous."""
        result = subprocess.run(
            ['uv', 'run', 'tqqq-sma'],
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Count alert/status lines
        alert_lines = [line for line in output.split('\n')
                      if any(x in line for x in ['ALERT:', 'STATUS:'])]

        # Should have at least one
        assert len(alert_lines) >= 1, "No alert/status lines found"

        # The last one should be the final status
        final_status = alert_lines[-1]
        assert any(x in final_status for x in ['BUY', 'SELL', 'Holding']), \
            f"Final status line unclear: {final_status}"

