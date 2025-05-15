queued tasks = 0, completed tasks = 2]
2025-05-15T23:23:05.927+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-5] o.s.web.servlet.DispatcherServlet        : POST "/api/image/remove-background", parameters={}
2025-05-15T23:23:05.965+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-5] s.w.s.m.m.a.RequestMappingHandlerMapping : Mapped to io.metaverse.fashion.studio.controller.ImageProcessingController#removeBackground(String)
2025-05-15T23:23:06.123+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-5] o.s.web.method.HandlerMethod             : Could not resolve parameter [0] in public org.springframework.http.ResponseEntity<?> io.metaverse.fashion.studio.controller.ImageProcessingController.removeBackground(java.lang.String): Required request parameter 'imageUrl' for method parameter type String is not present
2025-05-15T23:23:06.164+05:30  WARN 8076 --- [studio] [nio-8080-exec-5] .w.s.m.s.DefaultHandlerExceptionResolver : Resolved [org.springframework.web.bind.MissingServletRequestParameterException: Required request parameter 'imageUrl' for method parameter type String is not present]
2025-05-15T23:23:06.176+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-5] o.s.web.servlet.DispatcherServlet        : Completed 400 BAD_REQUEST


2: Error

2025-05-15T23:27:39.326+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-3] o.s.web.servlet.DispatcherServlet        : POST "/api/virtual-tryon/generate", parameters={multipart}
2025-05-15T23:27:39.397+05:30  WARN 8076 --- [studio] [nio-8080-exec-3] org.apache.catalina.connector.Request    : Creating the temporary upload location [C:\Users\DELL\AppData\Local\Temp\tomcat.8080.5630078631082919414\work\Tomcat\localhost\ROOT] as it is required by the servlet [dispatcherServlet]
2025-05-15T23:27:39.471+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-3] o.s.w.s.handler.SimpleUrlHandlerMapping  : Mapped to ResourceHttpRequestHandler [classpath [META-INF/resources/], classpath [resources/], classpath [static/], classpath [public/], ServletContext [/]]
2025-05-15T23:27:39.590+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-3] o.s.w.s.r.ResourceHttpRequestHandler     : Resource not found
2025-05-15T23:27:39.606+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-3] .w.s.m.s.DefaultHandlerExceptionResolver : Resolved [org.springframework.web.servlet.resource.NoResourceFoundException: No static resource api/virtual-tryon/generate.]
2025-05-15T23:27:39.610+05:30 DEBUG 8076 --- [studio] [nio-8080-exec-3] o.s.web.servlet.DispatcherServlet        : Completed 404 NOT_FOUND
