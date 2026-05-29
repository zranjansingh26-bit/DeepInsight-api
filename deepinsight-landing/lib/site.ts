export const site = {
  name: "DeepInsight",
  productName: "DeepInsight Starter Suite",
  tagline: "AI-Powered Analytics. Narrated for Decisions.",
  description:
    "DeepInsight turns spreadsheets, exports, and documents into decisions in five minutes. Rigorous analysis you can trust. Narration you can ship.",
  url: "https://app.deepinsight.ai",
};

export const nav = [
  { label: "Home", href: "#" },
  { label: "Features", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Testimonial", href: "#testimonials" },
  { label: "Pricing", href: "#pricing" },
];

export const trustedLogos = [
  "Northwind",
  "Helio",
  "Ironclad",
  "Cedar Run",
  "Bluepeak",
  "Atlas Co.",
];

export const partners = [
  "aws",
  "Google Analytics",
  "Grok",
  "OpenAI",
  "Polymath",
];

export const problems = [
  {
    title: "The Excel Wall",
    body:
      "Most businesses run on spreadsheets. Spreadsheets cannot surface trends, anomalies, or causes. Decisions are bounded by the literacy of whoever holds the file.",
    icon: "Sheet",
  },
  {
    title: "The Hiring Wall",
    body:
      "A capable analyst costs $90K-$130K. A data scientist $120K-$200K. Most SMBs cannot justify the hire, so insight either stalls or stays in heavyweight BI tools.",
    icon: "Users",
  },
  {
    title: "The Tool Sprawl Wall",
    body:
      "Shopify, Stripe, HubSpot, GA. Each shows one dashboard. None answers the cross-tool questions operators actually ask.",
    icon: "Layers",
  },
];

export const pillars = [
  {
    eyebrow: "Pillar 01",
    title: "Analyze It",
    subtitle: "The DS Pipeline",
    body:
      "Deterministic, numeric, reproducible. The DS Pipeline crunches your data and produces structured outputs that downstream consumers - your team, your reports, your dashboards - can rely on.",
    bullets: [
      "Auto quality scoring (0-100)",
      "Descriptive stats + correlation analysis",
      "5 anomaly methods (IQR, Z-score, IsoForest, LOF, DBSCAN)",
      "4 forecast models (SARIMA, Holt-Winters, MA, Prophet)",
      "AutoML across 6 supervised algorithms",
      "Clustering with auto-K + PCA visualisation",
    ],
    accent: "violet",
  },
  {
    eyebrow: "Pillar 02",
    title: "Explain It",
    subtitle: "The GenAI Pipeline",
    body:
      "Conversational, narrative, dataset-grounded. The GenAI Pipeline talks to your data the way a senior analyst would - and never hallucinates against your numbers.",
    bullets: [
      "Multi-LLM router: Claude, GPT-4o, Gemini",
      "Auto-grounded context built from your data",
      "Smart follow-up questions per turn",
      "Persistent sessions across days",
      "JSON-structured citations under every claim",
      "Provider failover with zero downtime",
    ],
    accent: "lavender",
  },
] as const;

export const features = [
  {
    eyebrow: "Upload Anything",
    title: "From spreadsheet to workspace in seconds.",
    body:
      "Drag in a CSV, XLSX, or JSON. DeepInsight parses, validates, scores quality, and gives you a private workspace. No data engineering required.",
    bullets: [
      "CSV / XLSX / XLS / JSON up to 50 MB",
      "UTF-8 + Latin-1 + Excel encodings",
      "Per-column quality, type, and null breakdown",
    ],
  },
  {
    eyebrow: "Quality Score",
    title: "Know if your data can be trusted - instantly.",
    body:
      "Every dataset is scored 0-100 across completeness, duplicates, and type consistency. The score gates downstream analysis so you never build on broken data.",
    bullets: [
      "Completeness, duplicates, type consistency",
      "Per-column null %, unique count, samples",
      "Warnings surfaced before charts are drawn",
    ],
  },
  {
    eyebrow: "Anomaly Detection",
    title: "Find the broken Saturday before your customer does.",
    body:
      "Five algorithms, one click. Univariate or multivariate. DeepInsight surfaces the outliers, classifies them, and explains why they matter.",
    bullets: [
      "IQR + Z-score for univariate signals",
      "Isolation Forest, LOF, DBSCAN for multivariate",
      "Auto-explained in plain English by the chat",
    ],
  },
  {
    eyebrow: "Forecasting",
    title: "A credible 'what next' with quantified uncertainty.",
    body:
      "SARIMA, Holt-Winters, Moving Average, and Prophet - applied to your time series with auto-detected frequency and seasonal period. Always with confidence intervals.",
    bullets: [
      "Auto date / value column detection",
      "Frequency + seasonality inferred",
      "Confidence bands on every forecast",
    ],
  },
  {
    eyebrow: "AutoML",
    title: "Train a real predictive model without writing code.",
    body:
      "Pick a target column. DeepInsight detects the problem type, preprocesses, fits 6 algorithms, tunes with GridSearchCV, applies SMOTE if needed, and serves the best model behind a prediction API.",
    bullets: [
      "Classification or regression, auto-detected",
      "Leaderboard across LR, RF, DT, XGB, SVM, KNN",
      "Persistent models with prediction logging",
    ],
  },
  {
    eyebrow: "Chat With Your Data",
    title: "A senior analyst, on call, in plain English.",
    body:
      "Ask why sales dropped, what is driving CAC, which customers are at risk. Answers are grounded in your dataset and followed by 2-3 smart next questions.",
    bullets: [
      "Multi-LLM (Claude / GPT-4o / Gemini)",
      "Auto-grounded context every turn",
      "Smart follow-up suggestions, ranked",
    ],
  },
];

export const stats = [
  { value: "5 min", label: "Time to first insight" },
  { value: "10+", label: "Analysis types" },
  { value: "3", label: "LLM providers" },
  { value: "0", label: "Data scientists required" },
];

export const useCases = [
  {
    key: "ecom",
    label: "Ecommerce",
    persona: "Ecommerce Operator",
    pain: "Cannot see which products, customers, and seasons actually drive margin.",
    outcome:
      "Upload Shopify exports. DeepInsight clusters customers, finds anomalies, forecasts demand, and recommends bundles. 6 hours of Excel becomes 10 minutes.",
  },
  {
    key: "marketing",
    label: "Marketing",
    persona: "Marketing Manager",
    pain: "Cannot explain why a channel's performance moved last quarter.",
    outcome:
      "Upload spend + conversion data. Get channel-by-channel CAC, attribution narrative, and a PDF that defends next quarter's budget.",
  },
  {
    key: "sales",
    label: "Sales",
    persona: "Sales Team Lead",
    pain: "Reports come too late and dashboards don't explain why quota slipped.",
    outcome:
      "Upload CRM exports. Ask 'why are we missing quota?'. AI identifies stage-by-stage conversion drift and recommends rep coaching priorities.",
  },
  {
    key: "ops",
    label: "Operations",
    persona: "Multi-Location Ops Analyst",
    pain: "Reconciling POS, labour, and inventory across 30 locations weekly.",
    outcome:
      "Upload daily POS + labour data. Forecast next week's demand per location, flag overstaffing anomalies, generate a one-page ops review automatically.",
  },
  {
    key: "consult",
    label: "Consultants",
    persona: "Independent Consultant",
    pain: "Manual deck-building does not scale; clients want more for less.",
    outcome:
      "Upload client data, generate exec-ready PDFs in minutes. Bill the same, deliver 3x the analysis, keep margin.",
  },
  {
    key: "smb",
    label: "SMB Owner",
    persona: "Owner-Operator",
    pain: "Decisions feel like guesses. Data is spread across 10 systems.",
    outcome:
      "One workspace, every export. Weekly auto-narratives surface what changed and what to do next.",
  },
];

export const plans = [
  {
    name: "Starter",
    price: 29,
    cadence: "/ month",
    annual: 23.2,
    description: "For solo operators and consultants getting started.",
    features: [
      "10 datasets",
      "1 seat",
      "1,000 chat messages / month",
      "All 10 analysis types",
      "JSON / HTML / PDF reports",
      "Community support",
    ],
    cta: "Start free trial",
    highlighted: false,
  },
  {
    name: "Pro",
    price: 79,
    cadence: "/ month",
    annual: 63.2,
    description: "For small teams, agencies, and growth marketers.",
    features: [
      "50 datasets",
      "5 seats",
      "10,000 chat messages / month",
      "PowerPoint export",
      "Scheduled analyses + alerts",
      "3 data connectors",
      "Document intelligence (100 pages)",
      "Email support",
    ],
    cta: "Start free trial",
    highlighted: true,
    ribbon: "Most popular",
  },
  {
    name: "Business",
    price: 249,
    cadence: "/ month",
    annual: 199,
    description: "For mid-market analytics teams that need scale and governance.",
    features: [
      "Unlimited datasets",
      "20 seats",
      "50,000 chat messages / month",
      "All data connectors",
      "Org accounts, RBAC, audit log",
      "BYO-LLM (Azure / Bedrock)",
      "Priority support + onboarding",
    ],
    cta: "Start free trial",
    highlighted: false,
  },
  {
    name: "Enterprise",
    price: null,
    cadence: "",
    annual: null,
    description: "For regulated industries and on-prem deployments.",
    features: [
      "Unlimited everything",
      "SSO (SAML / OIDC)",
      "On-prem / VPC deployment",
      "SOC 2 + GDPR + ISO 27001 evidence",
      "Dedicated CSM + SE",
      "Custom data connectors",
      "Annual contracts + procurement support",
    ],
    cta: "Talk to sales",
    highlighted: false,
  },
] as const;

export const testimonials = [
  {
    quote:
      "I had the monthly business review ready in twenty minutes. The narrative caught a regional anomaly we'd have missed for another week.",
    name: "<TBD>",
    role: "Head of Analytics",
    company: "<TBD>",
  },
  {
    quote:
      "DeepInsight is the closest thing I've used to having a senior data scientist in Slack. The follow-up questions are uncannily good.",
    name: "<TBD>",
    role: "Founder",
    company: "<TBD>",
  },
  {
    quote:
      "We replaced three tools - dashboarding, churn modelling, and exec-report writing - with one workspace. The math is still there if I want it.",
    name: "<TBD>",
    role: "VP Operations",
    company: "<TBD>",
  },
];

export const faqs = [
  {
    q: "What kinds of files can I upload?",
    a: "DeepInsight ingests CSV, XLSX, XLS, and JSON files up to 50 MB on Starter (and larger on Pro and above). Pro tiers add document intelligence for PDF, DOCX, and PowerPoint with structured extraction.",
  },
  {
    q: "Which LLMs does the chat use?",
    a: "We support Anthropic Claude (claude-3-haiku), OpenAI GPT-4o, and Google Gemini. The router picks based on configuration and automatically fails over if a provider is down. Business tier and above can BYO-LLM via Azure OpenAI or AWS Bedrock.",
  },
  {
    q: "Is my data used to train AI models?",
    a: "No. Your data is never used to train foundation models. LLM calls are routed under no-training agreements with each provider, and prompts are scoped to your workspace context only.",
  },
  {
    q: "How is data isolated between customers?",
    a: "Every table enforces Postgres Row-Level Security keyed on workspace ownership. Storage paths are user-folder-scoped. Even an application-layer bug cannot leak rows to the wrong owner.",
  },
  {
    q: "Can I cancel anytime?",
    a: "Yes. Monthly plans cancel at the end of the current billing cycle, annual plans get pro-rata refunds within 30 days. No salesperson required to downgrade.",
  },
  {
    q: "Do you offer a free trial?",
    a: "Yes - 14 days, no credit card. You get full access to the Pro tier limits during the trial; we email you on day 12 with options to keep going.",
  },
  {
    q: "How does AutoML work?",
    a: "Pick a target column. DeepInsight detects the problem type, preprocesses your data (imputation, encoding, scaling, SMOTE if imbalanced), trains six algorithms with GridSearchCV, and serves the best model behind a prediction endpoint.",
  },
  {
    q: "What about compliance?",
    a: "SOC 2 Type I is in progress (target Q3). GDPR is supported today. ISO 27001 and HIPAA-ready deployment options are part of the Enterprise roadmap.",
  },
];

export const footerColumns = [
  {
    title: "Solution",
    links: [
      { label: "Why DeepInsight", href: "#" },
      { label: "DeepInsight for iOS", href: "#" },
      { label: "Request a demo", href: "#" },
      { label: "Download", href: "#" },
    ],
  },
  {
    title: "Resources",
    links: [
      { label: "Blog", href: "#" },
      { label: "DeepInsight for iOS", href: "#" },
      { label: "DeepInsight Community", href: "#" },
      { label: "Support", href: "#" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About us", href: "#" },
      { label: "Legal", href: "#" },
      { label: "Privacy policy", href: "#" },
      { label: "Contact us", href: "#" },
    ],
  },
];
