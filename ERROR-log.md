2025-04-20T15:24:23.025+05:30 DEBUG 21820 --- [studio] [nio-8081-exec-6] o.s.web.servlet.DispatcherServlet        : "ERROR" dispatch for POST "/error?prompt=Black%20Half-Sleeve%20T-Shirt&style=casual", parameters={masked}
2025-04-20T15:24:23.027+05:30 DEBUG 21820 --- [studio] [nio-8081-exec-6] s.w.s.m.m.a.RequestMappingHandlerMapping : Mapped to org.springframework.boot.autoconfigure.web.servlet.error.BasicErrorController#error(HttpServletRequest)
2025-04-20T15:24:23.031+05:30 DEBUG 21820 --- [studio] [nio-8081-exec-6] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Using 'application/json', given [*/*] and supported [application/json, application/*+json, application/yaml]
2025-04-20T15:24:23.033+05:30 DEBUG 21820 --- [studio] [nio-8081-exec-6] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Writing [{timestamp=Sun Apr 20 15:24:23 IST 2025, status=500, error=Internal Server Error, path=/api/designs/ (truncated)...]
2025-04-20T15:24:23.041+05:30 DEBUG 21820 --- [studio] [nio-8081-exec-6] o.s.web.servlet.DispatcherServlet        : Exiting from "ERROR" dispatch, status 500


{
"timestamp": "2025-04-20T09:54:23.028+00:00",
"status": 500,
"error": "Internal Server Error",
"path": "/api/designs/generate"
}