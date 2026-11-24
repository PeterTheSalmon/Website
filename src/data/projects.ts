import type { ImageMetadata } from "astro";
import urboraLogo from "../assets/logos/urbora.svg";
import polityLogo from "../assets/logos/polity.png";
import munifyLogo from "../assets/logos/munify.svg";
import shotUrbora from "../assets/projects/urbora.ai.png";
import shotPolity from "../assets/projects/polity.coop.png";
import shotMunify from "../assets/projects/munify.ca.png";
import favChangemakers from "../assets/favicons/changemakerslibrary.org.svg";
import favAceguitar from "../assets/favicons/aceguitar.app.png";
import favAcis from "../assets/favicons/acislabs.ca.png";
import favKelowna from "../assets/favicons/kelownaboatcharters.ca.png";
import favCommunity from "../assets/favicons/communityassemblynetwork.ca.png";
import favSurvival from "../assets/favicons/survivalresearch.ca.png";
import crsLogo from "../assets/crs-logo.png";

export type Project = {
  name: string;
  href: string;
  domain: string;
  description: string;
  logo: ImageMetadata;
  screenshot?: ImageMetadata;
  team?: boolean;
  theme?: "urbora" | "polity" | "munify";
};

export const current: Project[] = [
  {
    name: "Urbora",
    href: "https://urbora.ai/",
    domain: "urbora.ai",
    description: "Plain-language answers about any property, with every source cited.",
    logo: urboraLogo,
    screenshot: shotUrbora,
    theme: "urbora",
  },
  {
    name: "Polity",
    href: "https://polity.coop/",
    domain: "polity.coop",
    description: "Tools for public engagement and group decision-making.",
    logo: polityLogo,
    screenshot: shotPolity,
    theme: "polity",
  },
  {
    name: "Munify",
    href: "https://munify.ca/",
    domain: "munify.ca",
    description: "Clear, sourced briefings from city council meetings.",
    logo: munifyLogo,
    screenshot: shotMunify,
    theme: "munify",
  },
];

export const earlier: Project[] = [
  {
    name: "Capital Reasoning",
    href: "https://capitalreasoning.com",
    domain: "capitalreasoning.com",
    description: "AI startup based in Victoria.",
    logo: crsLogo,
  },
  {
    name: "Changemakers Library",
    href: "https://changemakerslibrary.org",
    domain: "changemakerslibrary.org",
    description: "A video learning platform built for a University of Victoria course.",
    logo: favChangemakers,
  },
  {
    name: "AceGuitar",
    href: "https://aceguitar.app",
    domain: "aceguitar.app",
    description: "A guitar practice app with a tuner, metronome and chord library.",
    logo: favAceguitar,
  },
  {
    name: "ACIS Laboratories",
    href: "https://acislabs.ca/",
    domain: "acislabs.ca",
    description: "Website for UVic’s Advanced Control and Intelligent Systems Laboratories.",
    logo: favAcis,
  },
];

/** Shown behind "Show more" on the Work page. */
export const older: Project[] = [
  {
    name: "Kelowna Boat Charters",
    href: "https://kelownaboatcharters.ca",
    domain: "kelownaboatcharters.ca",
    description: "A refresh of the charter company’s site: layout, formatting and accessibility.",
    logo: favKelowna,
    team: true,
  },
  {
    name: "Survival Research Institute of Canada",
    href: "https://survivalresearch.ca",
    domain: "survivalresearch.ca",
    description: "A searchable public database of thousands of authors and publications.",
    logo: favSurvival,
    team: true,
  },
  {
    name: "Community Assembly Network",
    href: "https://communityassemblynetwork.ca",
    domain: "communityassemblynetwork.ca",
    description: "A WordPress site for sharing updates and growing a mailing list.",
    logo: favCommunity,
    team: true,
  },
];
