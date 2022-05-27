import React, { ReactElement, useCallback, useEffect } from "react";
import { Container } from "@mui/material";
import { useRouter } from "next/router";
import Head from "next/head";

import Footer from "./Footer";
import Header from "./Header";
import HeaderLinks from "./HeaderLinks";

interface LayoutProps {
  children?: ReactElement | ReactElement[];
  description?: string;
  keywords?: string;
  noHeader?: boolean;
  title?: string;
  url?: string;
}

let queryChecked = false;
function Layout(props: LayoutProps): ReactElement {
  const router = useRouter();

  useEffect(() => {
    if (typeof window !== "undefined" && router.isReady && !queryChecked) {
      queryChecked = true;
      let newApiKey: string | null = (router.query?.apiKey as string) || "",
        newApiPort: string | null = (router.query?.apiPort as string) || "9170",
        needUpdate = false;
      if (!router.query?.apiKey) {
        needUpdate = true;
        newApiKey = window.prompt("Please enter your API key", newApiKey);
      }
      if (!router.query?.apiPort) {
        needUpdate = true;
        newApiPort = window.prompt(
          "Please enter your API port (default: 9170)",
          newApiPort
        );
      }
      if (needUpdate && newApiKey && newApiPort) {
        const path = router.asPath.split("?")[0];
        router.replace({
          pathname:
            process.env.NODE_ENV === "development"
              ? path
              : path.includes(".html")
              ? path
              : `${path}.html`,
          query: {
            ...router.query,
            apiKey: newApiKey,
            apiPort: newApiPort,
          },
        });
      }
    }
  }, [router]);

  return (
    <>
      <Head>
        <title>
          {props.title ? `${props.title} - System Bridge` : `System Bridge`}
        </title>
        <link rel="canonical" href={props.url} />
        <meta
          name="description"
          content={
            props.description
              ? `${props.description}`
              : props.title
              ? `${props.title} - System Bridge`
              : `System Bridge`
          }
        />
        <meta
          name="keywords"
          content={
            props.keywords
              ? `${props.keywords}`
              : `system-bridge, system, bridge, typescript`
          }
        />
      </Head>
      {!props.noHeader && <Header />}
      {props.children}
    </>
  );
}

export default Layout;
