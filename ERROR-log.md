POST http://localhost:8080/api/users/login 401 (Unauthorized)

2025-05-18T19:06:51.444+05:30 DEBUG 3288 --- [studio] [nio-8080-exec-4] o.s.web.servlet.DispatcherServlet        : POST "/api/users/login", parameters={masked}
2025-05-18T19:06:51.446+05:30 DEBUG 3288 --- [studio] [nio-8080-exec-4] s.w.s.m.m.a.RequestMappingHandlerMapping : Mapped to io.metaverse.fashion.studio.controller.UserController#login(String, String)
Hibernate:
select
u1_0.id,
u1_0.email,
u1_0.password,
u1_0.username
from
users u1_0
where
u1_0.username=?
2025-05-18T19:06:51.478+05:30 DEBUG 3288 --- [studio] [nio-8080-exec-4] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Using 'application/json', given [*/*] and supported [application/json, application/*+json, application/yaml]
2025-05-18T19:06:51.481+05:30 DEBUG 3288 --- [studio] [nio-8080-exec-4] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Writing [{message=Invalid username or password}]
2025-05-18T19:06:51.493+05:30 DEBUG 3288 --- [studio] [nio-8080-exec-4] o.s.web.servlet.DispatcherServlet        : Completed 401 UNAUTHORIZED
