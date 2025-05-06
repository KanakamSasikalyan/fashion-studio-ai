
webpack compiled with 175 warnings
(node:7820) [DEP0060] DeprecationWarning: The `util._extend` API is deprecated. Please use Object.assign() instead.
Proxy error: Could not proxy request /api/virtual-tryon/try-on from localhost:3000 to http://localhost:8081/.
See https://nodejs.org/api/errors.html#errors_common_system_errors for more information (ECONNREFUSED).

react-dom.development.js:86 Warning: ReactDOM.render is no longer supported in React 18. Use createRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot

VirtualTryOn.jsx:29
POST http://localhost:3000/api/virtual-tryon/try-on 500 (Internal Server Error)
handleSubmit	@	VirtualTryOn.jsx:29
VirtualTryOn.jsx:37 Error submitting images: Error: Request failed with status code 500
at createError (createError.js:16:1)
at settle (settle.js:17:1)
at XMLHttpRequest.onloadend (xhr.js:54:1)
handleSubmit	@	VirtualTryOn.jsx:37
