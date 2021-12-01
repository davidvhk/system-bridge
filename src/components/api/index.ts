import { dirname } from "path";
import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger";
import { ExpressPeerServer } from "peer";
import { NestExpressApplication } from "@nestjs/platform-express";
import { NestFactory } from "@nestjs/core";
import { Server } from "http";
import AutoLaunch from "auto-launch";
import helmet from "helmet";

import { AppModule } from "./app.module";
import { Events } from "../events";
import { getConnection, getSettingsObject } from "../common";
import { HttpExceptionFilter } from "./http-exception.filter";
import { Logger } from "../logger";
import { MDNSAdversisement } from "../mdns/advertisement";
import { RequestInterceptor } from "./request.interceptor";
import { WsAdapter } from "./ws-adapter";

let app: NestExpressApplication,
  server: Server | undefined,
  rtc: { createRTCWindow: () => void; closeRTCWindow: () => boolean },
  events: Events;

export async function updateAppConfig(): Promise<void> {
  try {
    const connection = await getConnection();
    const settings = await getSettingsObject(connection);
    await connection.close();

    if (process.env.SB_PACKAGED !== "false") {
      const launchOnStartup: boolean =
        settings["general-launchOnStartup"] === "true";

      const autoLaunch = new AutoLaunch({
        name: "System Bridge",
        path: process.execPath,
      });
      if (launchOnStartup) await autoLaunch.enable();
      else await autoLaunch.disable();

      const { logger } = new Logger("API");
      logger.info(
        `Launch on startup: ${launchOnStartup} - ${
          (await autoLaunch.isEnabled()) ? "enabled" : "disabled"
        } - ${process.execPath}`
      );
      logger.close();
    }
  } catch (e) {
    const { logger } = new Logger("API");
    logger.error(e.message);
    logger.close();
  }
}

export async function startServer(): Promise<void> {
  const { logger } = new Logger("API");
  logger.info(
    [
      dirname(process.execPath),
      process.execPath,
      process.cwd(),
      JSON.stringify(process.argv),
      process.env.NODE_ENV,
      process.env.SB_CLI,
      process.env.SB_PACKAGED,
      process.env.SB_GUI,
    ].join(" - ")
  );
  logger.close();

  const connection = await getConnection();
  const settings = await getSettingsObject(connection);
  await connection.close();

  const apiPort = Number(settings["network-apiPort"]) || 9170;
  const wsPort = Number(settings["network-wsPort"]) || 9172;

  // Setup Nest.js app
  app = await NestFactory.create<NestExpressApplication>(AppModule, {
    logger: false,
  });

  app.useGlobalFilters(new HttpExceptionFilter());
  app.useGlobalInterceptors(new RequestInterceptor());

  // WS adapter
  app.useWebSocketAdapter(new WsAdapter(app, wsPort));

  // Enable security
  app.use(
    helmet({
      contentSecurityPolicy: false,
    })
  );
  // Enable CORS
  app.enableCors();

  // Setup Open API
  const document = SwaggerModule.createDocument(
    app,
    new DocumentBuilder()
      .setTitle("System Bridge")
      .setDescription("A bridge for your systems")
      .build()
  );
  SwaggerModule.setup("docs", app, document);

  // Get server from app
  server = app.getHttpServer();

  if (!server) {
    const { logger } = new Logger("API");
    logger.error("No server found! Aborting");
    logger.close();
    return;
  }

  server.on("error", (error: any) => {
    const { logger } = new Logger("API");
    logger.error(`Server error: ${error}`);
    logger.close();
  });
  server.on("listening", async () => {
    const { logger } = new Logger("API");
    logger.info(`API started on port ${apiPort}`);

    const mdnsAdvertisement = new MDNSAdversisement();
    await mdnsAdvertisement.createAdvertisement(apiPort, wsPort);
  });
  server.on("close", () => {
    const { logger } = new Logger("API");
    logger.info("Server closing.");
    logger.close();
  });

  await app.listen(apiPort);

  // Set up RTC Broker
  const apiKey = settings["network-apiKey"];
  if (typeof apiKey === "string") {
    const { logger } = new Logger("API");

    await updateAppConfig();

    const broker = ExpressPeerServer(server, {
      allow_discovery: true,
      key: apiKey,
    });
    broker.on("connection", (client) => {
      const { logger } = new Logger("API");
      logger.info(`Broker peer connected: ${client.getId()}`);
      logger.close();
    });
    broker.on("disconnect", (client) => {
      const { logger } = new Logger("API");
      logger.info(`Broker peer disconnected: ${client.getId()}`);
      logger.close();
    });
    app.use("/rtc", broker);
    logger.info(`RTC broker created on path ${broker.path()}`);

    events = new Events();
    events.setup(settings);
  }
  logger.close();
}

export async function stopServer(): Promise<void> {
  const { logger } = new Logger("API");
  if (app) {
    await app.close();
    logger.info("Nest Application closed.");
  }
  if (server) {
    server.close();
    logger.info("Server closed.");
  }
  logger.close();
  if (events) events.cleanup();
  if (rtc) rtc.closeRTCWindow();
  app = undefined;
  server = undefined;
  events = undefined;
  rtc = undefined;
}

process.on("uncaughtException", (error: any) => {
  const { logger } = new Logger("API");
  logger.error(`Uncaught Exception: ${error}`);
  logger.close();
});

(async () => {
  if (!app) startServer();
})();
