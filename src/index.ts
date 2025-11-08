/**
 * Cloudflare Workers - Pixel Pirates API
 * TypeScript version (fully supported)
 */

export interface Env {
	DB: D1Database;
	CACHE: KVNamespace;
	JWT_SECRET: string;
	API_KEY: string;
	ENVIRONMENT: string;
	DEBUG: string;
	APP_NAME: string;
	APP_VERSION: string;
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		const url = new URL(request.url);
		const method = request.method;

		// CORS headers
		const corsHeaders = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
			'Access-Control-Allow-Headers': 'Content-Type, Authorization',
			'Content-Type': 'application/json',
		};

		// Handle CORS preflight
		if (method === 'OPTIONS') {
			return new Response(null, {
				status: 204,
				headers: corsHeaders,
			});
		}

		try {
			// Health check
			if (url.pathname.includes('health')) {
				return jsonResponse({ status: 'healthy', service: 'Pixel Pirates API' }, corsHeaders);
			}

			// Root endpoint
			if (url.pathname === '/' || url.pathname === '/api/v1') {
				return jsonResponse(
					{
						name: env.APP_NAME,
						version: env.APP_VERSION,
						status: 'running',
						docs: '/docs',
						health: '/api/v1/health',
					},
					corsHeaders
				);
			}

			// Auth endpoints
			if (url.pathname.includes('/auth')) {
				return await handleAuth(request, env, corsHeaders);
			}

			// Analysis endpoints
			if (url.pathname.includes('/analyze')) {
				return await handleAnalysis(request, env, corsHeaders);
			}

			// Posts endpoints
			if (url.pathname.includes('/posts')) {
				return await handlePosts(request, env, corsHeaders);
			}

			// 404 Not found
			return jsonResponse({ error: 'Not found' }, corsHeaders, 404);
		} catch (error) {
			return jsonResponse(
				{
					error: 'Internal server error',
					detail: error instanceof Error ? error.message : 'Unknown error',
				},
				corsHeaders,
				500
			);
		}
	},
};

async function handleAuth(request: Request, env: Env, headers: HeadersInit): Promise<Response> {
	const url = new URL(request.url);
	const method = request.method;

	// Register
	if (url.pathname.includes('register') && method === 'POST') {
		try {
			const data = await request.json() as any;

			if (!data.email || !data.password) {
				return jsonResponse({ error: 'Email and password required' }, headers, 400);
			}

			// Simple password hashing (replace with bcrypt in production)
			const hashedPassword = `hashed_${data.password}`;

			const result = await env.DB.prepare(
				'INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)'
			)
				.bind(data.username || data.email, data.email, hashedPassword)
				.run();

			return jsonResponse(
				{
					message: 'User registered successfully',
					user_id: result.meta.last_row_id,
				},
				headers
			);
		} catch (error) {
			return jsonResponse(
				{ error: `Registration failed: ${error instanceof Error ? error.message : 'Unknown error'}` },
				headers,
				400
			);
		}
	}

	// Login
	if (url.pathname.includes('login') && method === 'POST') {
		try {
			const data = await request.json() as any;

			const result = await env.DB.prepare('SELECT * FROM users WHERE email = ?')
				.bind(data.email)
				.first();

			if (!result) {
				return jsonResponse({ error: 'Invalid credentials' }, headers, 401);
			}

			// Simple token (replace with JWT in production)
			const token = `token_${result.id}_${Date.now()}`;

			return jsonResponse(
				{
					access_token: token,
					token_type: 'bearer',
					user: {
						id: result.id,
						email: result.email,
						username: result.username,
					},
				},
				headers
			);
		} catch (error) {
			return jsonResponse(
				{ error: `Login failed: ${error instanceof Error ? error.message : 'Unknown error'}` },
				headers,
				500
			);
		}
	}

	return jsonResponse({ error: 'Method not allowed' }, headers, 405);
}

async function handleAnalysis(request: Request, env: Env, headers: HeadersInit): Promise<Response> {
	const method = request.method;

	if (method === 'POST') {
		try {
			const data = await request.json() as any;

			const content = data.content || '';
			if (!content) {
				return jsonResponse({ error: 'Content required' }, headers, 400);
			}

			// Simple analysis (replace with actual AI/ML)
			const contentLower = content.toLowerCase();
			let credibilityScore = 0.75;

			// Simple keyword-based detection
			const suspiciousKeywords = ['click here', 'act now', 'limited time', 'guaranteed', 'free money'];
			const foundSuspicious = suspiciousKeywords.some(keyword => contentLower.includes(keyword));

			if (foundSuspicious) {
				credibilityScore = 0.35;
			}

			const isMisinformation = credibilityScore < 0.5;

			// Cache result
			const cacheKey = `analysis_${hashString(content)}`;
			await env.CACHE.put(
				cacheKey,
				JSON.stringify({
					credibility_score: credibilityScore,
					is_misinformation: isMisinformation,
				}),
				{ expirationTtl: 3600 }
			);

			// Store in D1
			const userId = data.user_id || 1;

			// Insert post
			const postResult = await env.DB.prepare('INSERT INTO posts (user_id, content) VALUES (?, ?)')
				.bind(userId, content)
				.run();

			const postId = postResult.meta.last_row_id;

			// Insert analysis
			await env.DB.prepare(
				`INSERT INTO analysis_results
				(post_id, user_id, credibility_score, is_misinformation, confidence, analysis_type)
				VALUES (?, ?, ?, ?, ?, ?)`
			)
				.bind(postId, userId, credibilityScore, isMisinformation ? 1 : 0, 0.85, 'basic')
				.run();

			return jsonResponse(
				{
					post_id: postId,
					credibility_score: credibilityScore,
					is_misinformation: isMisinformation,
					confidence: 0.85,
					recommendation: isMisinformation
						? 'Verify with additional sources'
						: 'Content appears credible',
				},
				headers
			);
		} catch (error) {
			return jsonResponse(
				{ error: `Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}` },
				headers,
				500
			);
		}
	}

	return jsonResponse({ error: 'Method not allowed' }, headers, 405);
}

async function handlePosts(request: Request, env: Env, headers: HeadersInit): Promise<Response> {
	const method = request.method;

	if (method === 'GET') {
		try {
			const userId = 1; // Get from auth token in production

			const result = await env.DB.prepare(
				`SELECT p.*, a.credibility_score, a.is_misinformation
				FROM posts p
				LEFT JOIN analysis_results a ON p.id = a.post_id
				WHERE p.user_id = ?
				ORDER BY p.created_at DESC
				LIMIT 20`
			)
				.bind(userId)
				.all();

			return jsonResponse(
				{
					posts: result.results || [],
					count: result.results?.length || 0,
				},
				headers
			);
		} catch (error) {
			return jsonResponse(
				{ error: `Failed to fetch posts: ${error instanceof Error ? error.message : 'Unknown error'}` },
				headers,
				500
			);
		}
	}

	return jsonResponse({ error: 'Method not allowed' }, headers, 405);
}

function jsonResponse(data: any, headers: HeadersInit, status: number = 200): Response {
	return new Response(JSON.stringify(data), {
		status,
		headers,
	});
}

// Simple hash function for cache keys
function hashString(str: string): number {
	let hash = 0;
	for (let i = 0; i < str.length; i++) {
		const char = str.charCodeAt(i);
		hash = (hash << 5) - hash + char;
		hash = hash & hash;
	}
	return Math.abs(hash);
}
