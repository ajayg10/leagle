'use client'
/**
 * frontend/src/app/api/client.js
 *
 * Centralised Axios instance for all backend API calls.
 *
 * Request interceptor — attaches the Clerk JWT as an Authorization Bearer
 * token before every request.  Uses window.Clerk.session.getToken() which
 * is always available in a Clerk-wrapped app.
 *
 * Response interceptor:
 *   401 → redirects the user to the Clerk sign-in page.
 *   403 → throws an error with a user-readable message that the caller can
 *         display (e.g. in a toast or inline error state).
 */

import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor: attach Clerk JWT ─────────────────────────────────────
api.interceptors.request.use(
    async (config) => {
        try {
            // window.Clerk is populated by ClerkProvider in the root layout.
            let token = null
            if (typeof window !== 'undefined') {
                if (window.Clerk && !window.Clerk.loaded && typeof window.Clerk.load === 'function') {
                    try {
                        await window.Clerk.load()
                    } catch (_) {}
                }
                if (window.Clerk?.session) {
                    token = await window.Clerk.session.getToken()
                }
            }

            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`
            }
        } catch (err) {
            // Non-fatal: if we can't get the token, send the request unauthenticated.
            // The server will return 401 and the response interceptor below will
            // redirect to sign-in.
            console.warn('[api/client] Could not retrieve Clerk token:', err)
        }
        return config
    },
    (error) => Promise.reject(error),
)

// ── Response interceptor: handle 401 and 403 ─────────────────────────────────
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error?.response?.status

        if (status === 401) {
            if (error?.config?.skipAuthRedirect) {
                return Promise.reject(error)
            }
            // Session expired or never established — redirect to Clerk sign-in
            // Skip redirect if already on an auth page or public pages to prevent infinite loops
            if (typeof window !== 'undefined') {
                const path = window.location.pathname
                if (!path.startsWith('/sign-in') && !path.startsWith('/sign-up') && path !== '/' && !path.startsWith('/pricing') && !path.startsWith('/solutions') && !path.startsWith('/enterprise')) {
                    const returnUrl = encodeURIComponent(path)
                    window.location.href = `/sign-in?redirect_url=${returnUrl}`
                }
            }
            return Promise.reject(new Error('Your session has expired. Redirecting to sign-in…'))
        }

        if (status === 403) {
            return Promise.reject(
                new Error(
                    'You do not have permission to perform this action. ' +
                    'Administrator access is required.',
                ),
            )
        }

        return Promise.reject(error)
    },
)

// ── Regulations ───────────────────────────────────────────────────────────────
export const getRegulations = (params = {}) => api.get('/regulations/', { params })
export const getAvailableJurisdictions = () => api.get('/regulations/jurisdictions')
export const ingestRegulation = (data) => api.post('/regulations/ingest', data)
export const uploadRegulationPDF = (formData) =>
    api.post('/regulations/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
export const getSimilarRegulations = (id, topK = 5) =>
    api.get(`/regulations/${id}/similar?top_k=${topK}`)

// ── Policies ──────────────────────────────────────────────────────────────────
export const getPolicies = () => api.get('/policies/')
export const ingestPolicy = (data) =>
    api.post('/policies/ingest', data)
export const checkPolicyCompliance = (id) =>
    api.post(`/policies/${id}/compliance-check`)

// ── Impact ────────────────────────────────────────────────────────────────────
export const analyzeImpact = (regulationId, policyId) =>
    api.post(`/impact/analyze?regulation_id=${regulationId}&policy_id=${policyId}`)
export const getHeatmap = () => api.get('/impact/heatmap')
export const getImpactDetails = (dept, cat) => api.get(`/impact/details?dept=${dept}&cat=${cat}`)
export const getRegulationIntel = (id) => api.get(`/regulations/${id}/intel`)

// ── Alerts ────────────────────────────────────────────────────────────────────
export const getAlerts = () => api.get('/alerts/')
export const acknowledgeAlert = (id) => api.patch(`/alerts/${id}/acknowledge`)

// ── RAG ───────────────────────────────────────────────────────────────────────
export const askQuestion = (question) =>
    api.post('/rag/explain', { question })

// ── Ingestion & Analytics ──────────────────────────────────────────────────
export const uploadIngestFile = (formData, debug = false) =>
    api.post(`/ingest/upload${debug ? '?debug=true' : ''}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    })
export const runDocumentAnalysis = (documentId) =>
    api.post(`/analytics/compare/${encodeURIComponent(documentId)}`)

export default api
