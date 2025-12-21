# FloorEye Vercel Deployment Checklist

## Pre-Deployment

### 1. Environment Variables
- [ ] Copy `.env.example` to `.env.local` for local testing
- [ ] Set `VITE_API_BASE` to your Railway backend URL
  ```
  VITE_API_BASE=https://your-app.up.railway.app
  ```
- [ ] Verify no trailing slash on the URL

### 2. Local Verification
- [ ] Run `npm run dev` locally
- [ ] Open browser DevTools → Network tab
- [ ] Verify API calls go to the Railway backend (not localhost)
- [ ] Test at least one endpoint (e.g., `/history`)

### 3. Build Test
- [ ] Run `npm run build` to check for TypeScript errors
- [ ] Fix any compilation errors before deploying

---

## Vercel Deployment

### 4. Configure Environment Variables in Vercel
1. Go to Vercel Dashboard → Project → Settings → Environment Variables
2. Add the following variable:
   ```
   Name:  VITE_API_BASE
   Value: https://your-railway-app.up.railway.app
   ```
3. Select environments: **Production**, **Preview**, **Development**
4. Click **Save**

### 5. Trigger Deployment
- [ ] Push code to main branch, or
- [ ] Trigger manual redeploy from Vercel Dashboard

### 6. Verify Build Logs
- [ ] Check Vercel build logs for errors
- [ ] Confirm successful build completion

---

## Post-Deployment Verification

### 7. Test Live API Integration
- [ ] Open deployed Vercel URL
- [ ] Open browser DevTools → Network tab
- [ ] Navigate to pages that make API calls
- [ ] Verify requests go to Railway backend URL
- [ ] Confirm responses return expected data (200 OK)

### 8. Test Each Feature
- [ ] **History Page**: Detection history loads with images
- [ ] **Email Recipients**: List, add, toggle, delete work correctly
- [ ] **Cameras**: Camera list loads (if applicable)
- [ ] **Detection**: Frame detection works (if applicable)

### 9. Error Handling
- [ ] Test with invalid data (graceful error handling)
- [ ] Check console for any CORS errors
- [ ] Verify error messages are user-friendly

---

## Troubleshooting

### CORS Issues
If you see CORS errors, verify:
1. Backend has CORS middleware with `allow_origins=["*"]`
2. Railway backend is accessible via HTTPS
3. Frontend is using the correct Railway URL

### API Calls to localhost
If API still goes to localhost:
1. Ensure VITE_API_BASE is set in Vercel (not VITE_API_BASE_URL)
2. Redeploy after adding environment variable
3. Clear browser cache and hard refresh

### Network Errors
1. Check Railway backend is running (`GET /` should return status)
2. Verify Railway URL is correct and accessible
3. Check Railway logs for backend errors

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history?limit=&offset=` | Fetch detection history |
| GET | `/history/{id}/image` | Get event image |
| GET | `/email-recipients` | List recipients |
| POST | `/email-recipients` | Add recipient |
| PATCH | `/email-recipients/{id}` | Toggle active |
| DELETE | `/email-recipients/{id}` | Remove recipient |
