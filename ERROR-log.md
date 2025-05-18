2025-05-18T16:19:02.183+05:30 DEBUG 13548 --- [studio] [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : POST "/api/users/login", parameters={masked}
2025-05-18T16:19:02.198+05:30 DEBUG 13548 --- [studio] [nio-8080-exec-1] s.w.s.m.m.a.RequestMappingHandlerMapping : Mapped to io.metaverse.fashion.studio.controller.UserController#login(String, String)
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
2025-05-18T16:19:03.715+05:30 DEBUG 13548 --- [studio] [nio-8080-exec-1] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Using 'text/plain', given [*/*] and supported [text/plain, */*, application/json, application/*+json, application/yaml]
2025-05-18T16:19:03.724+05:30 DEBUG 13548 --- [studio] [nio-8080-exec-1] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Writing ["Invalid username or password"]
2025-05-18T16:19:03.747+05:30 DEBUG 13548 --- [studio] [nio-8080-exec-1] o.s.web.servlet.DispatcherServlet        : Completed 401 UNAUTHORIZED
