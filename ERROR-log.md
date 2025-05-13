2025-05-13T18:09:08.812+05:30 DEBUG 5476 --- [studio] [nio-8080-exec-5] o.s.web.servlet.DispatcherServlet        : POST "/api/virtual-try-on/start", parameters={multipart}
2025-05-13T18:09:08.914+05:30 DEBUG 5476 --- [studio] [nio-8080-exec-5] s.w.s.m.m.a.RequestMappingHandlerMapping : Mapped to io.metaverse.fashion.studio.controller.CamVirtualTryOnController#startVirtualTryOn(MultipartFile, int)
Starting Python process for virtual try-on...
Executing command: python src/main/resources/python/cam_virtual_tryon_service.py --cloth C:\Users\DELL\AppData\Local\Temp\tryon-cloth-5000974772483996325.png --port 8765
2025-05-13T18:09:09.095+05:30 DEBUG 5476 --- [studio] [nio-8080-exec-5] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Found 'Content-Type:application/json' in response
2025-05-13T18:09:09.098+05:30 DEBUG 5476 --- [studio] [nio-8080-exec-5] o.s.w.s.m.m.a.HttpEntityMethodProcessor  : Writing ["{"message": "Virtual try-on started successfully", "port": 8765}"]
2025-05-13T18:09:09.140+05:30 DEBUG 5476 --- [studio] [nio-8080-exec-5] o.s.web.servlet.DispatcherServlet        : Completed 200 OK
[Python Process] INFO:websockets.server:server listening on 127.0.0.1:8765
[Python Process] INFO:websockets.server:server listening on [::1]:8765
[Python Process] INFO:websockets.server:connection open
[Python Process] ERROR:websockets.server:connection handler failed
[Python Process] Traceback (most recent call last):
[Python Process]   File "C:\Users\DELL\AppData\Local\Programs\Python\Python310\lib\site-packages\websockets\asyncio\server.py", line 376, in conn_handler
[Python Process]     await self.handler(connection)
[Python Process] TypeError: main.<locals>.<lambda>() missing 1 required positional argument: 'path'
