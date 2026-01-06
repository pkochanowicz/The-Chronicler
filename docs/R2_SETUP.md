# Cloudflare R2 Setup Guide

**Quick setup guide for connecting The Chronicler to Cloudflare R2 image storage.**

---

## Why R2?

Cloudflare R2 provides **free, permanent image hosting** for character portraits:
- ✅ **10 GB free storage** (more than enough for 1000+ portraits)
- ✅ **Unlimited downloads** (zero egress fees)
- ✅ **No credit card required** for free tier
- ✅ **Production-grade CDN** with global delivery

---

## Setup Steps

### 1. Create Cloudflare Account

1. Go to https://dash.cloudflare.com/sign-up
2. Sign up (free, no credit card needed)
3. Verify your email

### 2. Create R2 Bucket

1. In Cloudflare dashboard, click **R2** in the sidebar
2. Click **Create bucket**
3. Configure:
   - **Name**: `azeroth-bound-images` (or your preferred name)
   - **Location**: Automatic (recommended)
4. Click **Create bucket**

### 3. Enable Public Access

1. Open your bucket: `azeroth-bound-images`
2. Go to **Settings** tab
3. Scroll to **Public Access**
4. Click **Allow Access**
5. **Copy your public bucket URL**: `https://pub-XXXXXXXXXX.r2.dev`
   - Save this! You'll need it for environment variables

### 4. Create API Token

1. In R2 dashboard, click **Manage R2 API Tokens**
2. Click **Create API Token**
3. Configure:
   - **Token name**: `chronicler-bot`
   - **Permissions**: ✅ Object Read & Write
   - **Bucket**: Select `azeroth-bound-images`
   - **TTL**: Never expire (or custom expiry)
4. Click **Create API Token**
5. **IMPORTANT**: Copy these values immediately (they won't be shown again):
   - **Access Key ID**: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - **Secret Access Key**: `YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY`
   - **Account ID**: (shown at top of page)

### 5. Configure Environment Variables

#### For Local Development (`.env` file):

Add these lines to your `.env` file:

```bash
# Cloudflare R2 Configuration
R2_ACCOUNT_ID=your_account_id_here
R2_ACCESS_KEY_ID=your_access_key_id_here
R2_SECRET_ACCESS_KEY=your_secret_access_key_here
R2_BUCKET_NAME=azeroth-bound-images
R2_PUBLIC_URL=https://pub-XXXXXXXXXX.r2.dev
```

**Replace:**
- `your_account_id_here` → Account ID from step 4
- `your_access_key_id_here` → Access Key ID from step 4
- `your_secret_access_key_here` → Secret Access Key from step 4
- `https://pub-XXXXXXXXXX.r2.dev` → Your public bucket URL from step 3

#### For Production (Fly.io):

Set secrets using Fly CLI:

```bash
flyctl secrets set \
  R2_ACCOUNT_ID=your_account_id_here \
  R2_ACCESS_KEY_ID=your_access_key_id_here \
  R2_SECRET_ACCESS_KEY=your_secret_access_key_here \
  R2_BUCKET_NAME=azeroth-bound-images \
  R2_PUBLIC_URL=https://pub-XXXXXXXXXX.r2.dev
```

### 6. Test the Connection

Run a quick test to verify R2 is configured correctly:

```bash
# Start your bot locally
poetry run python main.py

# Watch logs for R2 connection confirmation
# You should see: "Image storage configured: Cloudflare R2 (azeroth-bound-images)"
```

Try uploading a character portrait via `/register_character` command. The bot will upload it to R2 and return a permanent CDN URL.

---

## Troubleshooting

### Error: "Bucket not found"
- **Solution**: Check that `R2_BUCKET_NAME` matches exactly (case-sensitive)
- Verify bucket exists in Cloudflare dashboard

### Error: "Access denied"
- **Solution**: Check API token permissions
- Ensure token has **Object Read & Write** for your bucket
- Verify `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY` are correct

### Error: "Invalid endpoint"
- **Solution**: Check `R2_ACCOUNT_ID` is correct
- Account ID is shown at top of R2 dashboard

### Images return 403 Forbidden
- **Solution**: Enable Public Access on your bucket
- Settings → Public Access → Allow Access

### Bot uses default portrait instead of uploads
- **Solution**: Check logs for R2 errors
- Bot falls back to default portrait if R2 upload fails
- Verify all 5 R2 environment variables are set

---

## Monitoring Usage

View your R2 usage in Cloudflare dashboard:
1. Go to **R2** in dashboard
2. Click your bucket
3. Go to **Metrics** tab

**Free tier limits:**
- Storage: 10 GB/month
- Class A operations (uploads): 1,000,000/month
- Class B operations (downloads): 10,000,000/month
- Egress: **Unlimited (free)**

For typical guild usage (~100 characters), you'll use:
- **Storage**: ~50 MB (0.5% of limit)
- **Uploads**: ~100/month (0.01% of limit)
- **Downloads**: ~10,000/month (0.1% of limit)

---

## Security Best Practices

1. **Never commit secrets to git**
   - `.env` is in `.gitignore` (already configured)
   - Use environment variables or Fly.io secrets

2. **Rotate API keys every 90 days**
   - Create new token in Cloudflare
   - Update `.env` or Fly secrets
   - Delete old token

3. **Use read-only public access**
   - Public access only allows downloading images
   - Uploads require API token (bot only)

---

## Next Steps

- ✅ **R2 configured** → Character portraits will now be stored permanently
- 📖 See [IMAGE_STORAGE.md](./IMAGE_STORAGE.md) for technical implementation details
- 🧪 See [tests/services/test_image_storage.py](../tests/services/test_image_storage.py) for testing

---

**Setup Complete!** 🎉

Character portraits will now be uploaded to Cloudflare R2 with permanent, fast CDN URLs.
