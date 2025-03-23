# TrustResearch

## Introduction
Academic integrity is fundamental to the credibility of research publications. However, fraudulent practices such as unverifiable claims, misleading citations, and citation padding have become increasingly prevalent. These issues undermine the trustworthiness of scientific literature and make the review process more challenging.

**TrustResearch** is a novel AI and blockchain-based system designed to enhance the credibility of research publications by detecting fraudulent behavior in submitted manuscripts. The system employs AI to validate research claims and uses blockchain technology for secure and immutable storage. Additionally, it utilizes graph-based citation analysis to assess the relevance of cited works, thereby identifying potentially misleading or unrelated references.

**Unverifiable research claims** refer to assertions made in a manuscript that lack supporting evidence in the form of referenced artifacts, such as nanopublications or datasets provided by the author. TrustResearch does not attempt to replicate or deeply parse the paper's content. Instead, it intends to check whether claims reference verifiable digital artifacts and flags those that do not. For example, a claim like “our method improves accuracy by 20%” would be flagged if no dataset or nanopublication is linked to substantiate it. This keeps the validation lightweight while encouraging transparency and reproducibility.

---

## What would be the “Demo” of the project?

The demo will illustrate how **TrustResearch** enhances research integrity by detecting fraudulent claims and verifying citations. It will involve the following key steps:

### 1. Manuscript Submission:
- A researcher submits a paper to the system for verification.
- The manuscript is stored securely on **IPFS**, with a hash recorded on the **Ethereum blockchain** for tamper-proof verification.

### 2. Automated Claim Validation (AI Component):
- The system extracts key claims from the manuscript and cross-references them with **associated artifacts** such as nanopublications, code, and datasets.
- AI evaluates whether the claims are **internally verifiable**. Claims not traceable to any evidence within the paper or its artifacts are flagged as unverifiable.

### 3. Graph-Based Citation Analysis:
- A graph-based citation network is constructed to assess the relevance of cited works.
- The system identifies instances of:
  - **Citation padding**: excessive or unrelated citations used to artificially inflate impact.
  - **Misleading references**: citations that do not support the claim they are linked to.
  - **Citation collusion**: when a cluster of papers from the same group or network frequently cite each other without substantial relevance.  
    **Example:** Three research groups consistently citing each other’s work to inflate metrics without contributing new or distinct ideas. TrustResearch clusters these citation patterns and lowers their credibility score.

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
- **For Researchers:** They receive feedback on their manuscript's credibility before submission.
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
