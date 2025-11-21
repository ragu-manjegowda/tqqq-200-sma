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
        lines = output.split('\n')

        # Simulate grep commands from workflow
        def grep_pattern(pattern, lines):
            """Simulate grep with pattern."""
            for line in lines:
                if re.search(pattern, line):
                    return line.strip()
            return None

        # Extract using workflow patterns
        signal = grep_pattern(r'(ALERT: BUY|ALERT: SELL|STATUS: Holding)', lines)
        date = grep_pattern(r'Date:', lines)
        qqq_close = grep_pattern(r'QQQ Close:', lines)
        tqqq_close = grep_pattern(r'TQQQ Close:', lines)
        sma200 = grep_pattern(r'SMA200:', lines)
        qqq_vs_sma = grep_pattern(r'QQQ vs SMA200:', lines)
        buy_threshold = grep_pattern(r'BUY Threshold', lines)
        sell_threshold = grep_pattern(r'SELL Threshold', lines)
        position = grep_pattern(r'Position:', lines)

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

        # Verify none are empty strings
        assert len(signal) > 0, "Signal is empty"
        assert len(date) > 0, "Date is empty"
        assert len(qqq_close) > 0, "QQQ close is empty"
        assert len(tqqq_close) > 0, "TQQQ close is empty"
        assert len(sma200) > 0, "SMA200 is empty"
        assert len(qqq_vs_sma) > 0, "QQQ vs SMA is empty"
        assert len(buy_threshold) > 0, "Buy threshold is empty"
        assert len(sell_threshold) > 0, "Sell threshold is empty"
        assert len(position) > 0, "Position is empty"


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

