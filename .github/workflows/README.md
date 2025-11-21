# GitHub Actions Workflows

This directory contains automated workflows for the TQQQ 200-Day SMA trading system.

## 📋 Available Workflows

### 1. **Test Workflow** (`test.yml`)

**Triggers**: On every push and pull request to main/master/develop branches

**What it does**:
- ✅ Runs all 72 unit tests
- ✅ Generates code coverage report
- ✅ Uploads coverage artifacts
- ✅ Displays test summary in GitHub UI

**Status Badge**:
```markdown
![Tests](https://github.com/YOUR_USERNAME/tqqq-sma/workflows/Run%20Tests/badge.svg)
```

---

### 2. **Daily Signal Workflow** (`daily-signal.yml`)

**Triggers**: 
- 🕐 Automatically at **9:10 PM UTC** (4:10 PM ET) every weekday
- 🔘 Manually via "Run workflow" button

**What it does**:
- 📊 Fetches latest market data from Yahoo Finance
- 🧮 Calculates 200-day SMA and trading signals
- 📈 Displays current signal in GitHub Actions summary
- 🚨 **Creates GitHub Issue** on BUY/SELL signals
- 📧 **Sends GitHub notification** on BUY/SELL alerts
- 💾 Uploads signal output and trade log as artifacts

**How notifications work**:
- **HOLD status**: Workflow succeeds ✅ (no notification)
- **BUY/SELL signal**: Workflow "fails" ❌ (triggers GitHub notification)
- **Issue created**: Automatic GitHub issue with signal details
- **Email alert**: GitHub sends email if you have notifications enabled

---

## 🔔 Setting Up Notifications

### 1. Enable GitHub Notifications

Go to your GitHub settings:
1. Navigate to **Settings** → **Notifications**
2. Enable **Email** or **Web** notifications for:
   - ✅ **Actions** (for workflow failures)
   - ✅ **Issues** (for signal issues)
3. Ensure **Watching** is enabled for your repository

### 2. Configure Repository Notifications

On your repository page:
1. Click **Watch** (top-right)
2. Select **All Activity** or **Custom**
3. If Custom, enable:
   - ✅ **Issues** (for signal alerts)
   - ✅ **Actions** (for workflow runs)

### 3. Email Notification Settings

You'll receive emails when:
- 🟢 **BUY signal detected** → Issue created + Workflow "fails"
- 🔴 **SELL signal detected** → Issue created + Workflow "fails"
- ⚪ **HOLD status** → No notification (quiet operation)

---

## 📊 Viewing Daily Signals

### GitHub Actions Summary

After each run:
1. Go to **Actions** tab in your repository
2. Click on latest **Daily TQQQ Signal** workflow run
3. View the summary with:
   - Current date and market data
   - QQQ, TQQQ prices
   - 200-day SMA value
   - Buy/sell thresholds
   - Current position
   - Trading signal status

### Signal History

All signals are preserved:
- **Issues**: Tagged with `trading-signal`, `buy`, or `sell` labels
- **Artifacts**: Signal output files kept for 90 days
- **CSV Log**: Trade history in `signals_log.csv` artifact

---

## 🔧 Manual Trigger

To run the signal check manually:

1. Go to **Actions** tab
2. Select **Daily TQQQ Signal** workflow
3. Click **Run workflow** button
4. Select branch (usually `main`)
5. Click green **Run workflow** button

This is useful for:
- Testing the workflow
- Checking signal outside market hours
- Verifying setup after changes

---

## 📅 Schedule Details

### Market Hours
- **US Market Close**: 4:00 PM ET / 1:00 PM PT / 9:00 PM UTC
- **Workflow Runs**: 4:10 PM ET / 1:10 PM PT / 9:10 PM UTC
- **Days**: Monday-Friday (weekdays only)

### Cron Expression
```yaml
cron: '10 21 * * 1-5'
```
- `10`: Minute (10)
- `21`: Hour (9 PM UTC)
- `*`: Any day of month
- `*`: Any month
- `1-5`: Monday through Friday

---

## 🛠️ Customization

### Change Run Time

Edit `daily-signal.yml`:
```yaml
schedule:
  - cron: '10 21 * * 1-5'  # Change time here
```

**Time converter**:
- 4:00 PM ET = 21:00 UTC (standard time)
- 4:00 PM ET = 20:00 UTC (daylight saving time)

### Disable Notifications

To run without notifications on signals:
1. Remove the `exit 1` lines in the signal detection step
2. Or remove the issue creation steps

### Add More Notification Methods

You can extend the workflow to:
- Send Slack notifications
- Send Discord notifications
- Send Telegram messages
- Post to Twitter/X
- Send SMS via Twilio

Example for Slack:
```yaml
- name: Send Slack notification
  if: steps.signal.outputs.alert_type != 'HOLD'
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "TQQQ Signal: ${{ steps.signal.outputs.alert_type }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🔒 Security Notes

### Secrets

This workflow doesn't require secrets by default, but if you add:
- Email notifications (SMTP)
- Slack/Discord webhooks
- API keys

Add them in **Settings** → **Secrets and variables** → **Actions**

### Permissions

The workflow needs:
- ✅ **Read** access to repository (checkout code)
- ✅ **Write** access to issues (create signal issues)
- ✅ **Write** access to actions (upload artifacts)

These are granted by default in GitHub Actions.

---

## 📝 Artifacts

Each workflow run saves:
- `signal_output.txt` - Full console output
- `signals_log.csv` - Historical trade log
- `coverage-report/` - HTML coverage report (test workflow)

**Retention**:
- Daily signals: 90 days
- Coverage reports: 30 days

---

## 🐛 Troubleshooting

### Workflow Not Running

**Check**:
1. Is repository public or do you have Actions enabled?
2. Is the workflow file in `.github/workflows/`?
3. Are you pushing to `main`/`master` branch?
4. Check **Actions** tab for any errors

### Not Receiving Notifications

**Check**:
1. GitHub notification settings enabled?
2. Email verified in GitHub?
3. Repository watch settings correct?
4. Check spam folder for GitHub emails

### Signal Detection Issues

**Check**:
1. View workflow run logs in Actions tab
2. Download `signal_output.txt` artifact
3. Check if market data fetched successfully
4. Verify Yahoo Finance API is accessible

### Manual Run Not Working

**Check**:
1. Do you have write access to repository?
2. Is workflow file valid YAML?
3. Try pushing a small change to trigger automatic run

---

## 📚 Example Notification Email

When a BUY signal is detected, you'll receive:

**Subject**: `[tqqq-sma] Daily TQQQ Signal failed`

**Body**:
```
The workflow Daily TQQQ Signal run #123 failed.

View details: https://github.com/YOUR_USERNAME/tqqq-sma/actions/runs/...
```

Additionally, a new issue will be created:

**Subject**: `🟢 TQQQ BUY SIGNAL - 2025-11-22`

**Body**: Full signal details with market data, thresholds, and action required

---

## 🎯 Best Practices

1. **Watch the repository** to receive all notifications
2. **Check Actions summary** daily to see signal status
3. **Review issue history** to see signal timeline
4. **Download artifacts** if you want historical data
5. **Test manually** after setup to verify notifications work

---

## 📖 Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Cron Schedule Expression](https://crontab.guru/)
- [GitHub Notifications Settings](https://docs.github.com/en/account-and-profile/managing-subscriptions-and-notifications-on-github)

---

**Last Updated**: November 2025

