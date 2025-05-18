queued tasks = 0, completed tasks = 2]
2025-05-18T17:56:16.575+05:30 DEBUG 16404 --- [studio] [nio-8080-exec-5] o.s.web.servlet.DispatcherServlet        : POST "/api/auth/signup", parameters={}
2025-05-18T17:56:16.643+05:30 DEBUG 16404 --- [studio] [nio-8080-exec-5] o.s.w.s.handler.SimpleUrlHandlerMapping  : Mapped to ResourceHttpRequestHandler [classpath [META-INF/resources/], classpath [resources/], classpath [static/], classpath [public/], ServletContext [/]]
2025-05-18T17:56:16.983+05:30 DEBUG 16404 --- [studio] [nio-8080-exec-5] o.s.w.s.r.ResourceHttpRequestHandler     : Resource not found
2025-05-18T17:56:17.295+05:30 DEBUG 16404 --- [studio] [nio-8080-exec-5] .w.s.m.s.DefaultHandlerExceptionResolver : Resolved [org.springframework.web.servlet.resource.NoResourceFoundException: No static resource api/auth/signup.]
2025-05-18T17:56:17.301+05:30 DEBUG 16404 --- [studio] [nio-8080-exec-5] o.s.web.servlet.DispatcherServlet        : Completed 404 NOT_FOUND


Signup.jsx:15
POST http://localhost:8080/api/auth/signup 403 (Forbidden)
handleSubmit	@	Signup.jsx:15

Signup.jsx:31 Error during signup: SyntaxError: Failed to execute 'json' on 'Response': Unexpected end of JSON input
at handleSubmit (Signup.jsx:27:1)
handleSubmit	@	Signup.jsx:31