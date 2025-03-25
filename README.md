# TrustResearch

## Introduction
Academic integrity is fundamental to the credibility of research publications. However, fraudulent practices such as unverifiable claims, misleading citations, and citation padding have become increasingly prevalent. These issues undermine the trustworthiness of scientific literature and make the review process more challenging.

**TrustResearch** is a novel AI and blockchain-based system designed to enhance the credibility of research publications by detecting fraudulent behavior in submitted manuscripts. The system employs AI to validate ML related research claims and uses blockchain technology for secure and immutable storage. Additionally, it utilizes graph-based citation analysis to assess the relevance of cited works, thereby identifying potentially misleading or unrelated references.

**Unverifiable research claims** are statements in a manuscript that cite external sources or artifacts but lack verifiable support from those sources. TrustResearch does not attempt to deeply parse or replicate the paper's content. Instead, it checks whether each claim references an existing digital artifact — such as a nanopublication, dataset, or result.

To ensure scalability, TrustResearch avoids complex content parsing or experiment replication. Instead, it uses a lightweight verification model based on author-submitted claim-to-artifact mappings. Each research claim must be explicitly linked to a digital artifact — such as a nanopublication, dataset, or result summary — which is validated for structure and existence.
This approach allows TrustResearch to scale to millions of papers without requiring heavy computation. Claims are treated as verifiable if they are correctly mapped to a structured artifact. The system optionally stores claim hashes on a blockchain for long-term integrity and traceability, enabling reviewers or institutions to audit the links without needing to process full documents.

Additionally, TrustResearch flags **citation collusion**, which occurs when a group of papers repeatedly cite each other to artificially inflate credibility or impact. For instance, if Paper A cites B, B cites C, and C cites A — and this loop contains minimal external references — the system identifies it as a collusion cluster and lowers its citation credibility score.


---

## What would be the “Demo” of the project?

The demo will illustrate how **TrustResearch** enhances research integrity by detecting fraudulent claims and verifying citations. It will involve the following key steps:

### 1. Manuscript Submission:
- A researcher submits a paper to the system for verification.
- The manuscript alogn with claims, datasets, and other related contents are stored securely on **IPFS**, with a hash recorded on the **Ethereum blockchain** for tamper-proof verification.

### 2. Automated Claim Validation (AI Component):
- The system extracts key claims from the manuscript and validates by running the validation code on corresponding datasets, modela and hyperparameters.
- AI evaluates whether the claims are **internally verifiable**. Claims not traceable to any evidence within the paper are flagged as unverifiable.

### 3. Graph-Based Citation Analysis:
- A graph-based citation network is constructed to assess the relevance of cited works.
- The system identifies instances of:
  - **Citation padding**: excessive or potentially unrelated citations used to artificially inflate impact, especially if the author is citing their own papers continuously.
  - **Citation collusion**: when a cluster of papers from the same group or network frequently cite each other, potentially without substantial relevance.  
    **Example:** Three research groups consistently citing each other’s work to inflate metrics. TrustResearch clusters these citation patterns and lowers their credibility score.

### 4. Fraud Detection and Report Generation:
- The system generates an **integrity report** highlighting potential issues:
  - Unverifiable claims  
  - Citation padding  
  - Collusion clusters
- Reviewers can access **AI-driven insights** to assist in their evaluation.

### 5. Blockchain-Based Transparency:
- Once a paper is verified, its metadata (**author details, verification results**) is stored securely on the blockchain, ensuring immutability.
- Reviewers and journal editors can retrieve verification records to maintain research credibility.

---

## Expected Outcome
- **For Researchers:** They receive feedback on their manuscript's credibility.
- **For Reviewers:** The system simplifies fraud detection, reducing manual effort.
- **For Journals:** A transparent, blockchain-based system ensures research integrity.
- **For the Scientific Community:** Increased trust in published research.

---

## End-Users
The primary end-users of **TrustResearch** include:
- **Academic Reviewers** – Using AI-driven insights to assess research credibility.
- **Journal Editors** – Verifying integrity before accepting papers.
- **Researchers** – Ensuring their work is correctly cited and validated before submission.
- **Funding Agencies & Universities** – Ensuring research output meets ethical standards.

---

## Responsibilities of Team Members

| Team Member              | Role & Responsibilities                                                                 |
|--------------------------|------------------------------------------------------------------------------------------|
| **Ben Manicke**          | Communicating between Blockchain & Backend and connecting them with frontend.            |
| **Md Motaleb Hossen Manik** | Developing Blockchain and IPFS part for claim verification.                           |
| **Josh Youngbar**        | Developing Graph-based architecture and implementing AI part for citation fraud detection. |

---

## Team Member Coordination
- **Meeting Time:** **Wednesday at 12:00 PM at Union.**

## Communication Channel
- **Primary platform:** **Discord** for daily discussions and quick updates.
