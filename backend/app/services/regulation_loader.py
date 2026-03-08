"""
Regulation Knowledge Base Loader.

Populates the database with structured regulation data for:
  - EU AI Act (Articles 5,6,9,10,11,13,14,15,26,49,50,52,62,71,99 + Annexes I-III)
  - US Regulations (NYC LL144, Colorado SB205, FTC AI Guidelines, EEOC AI Guidance)
  - GDPR AI-relevant articles (6,9,13,14,22,35)
  - India DPDP Act (Sections 4,5,6,7,8,9,11)
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.store.models import Regulation


# ---------------------------------------------------------------------------
# Regulation data definitions
# ---------------------------------------------------------------------------

def _eu_ai_act_regulations() -> List[dict]:
    return [
        {
            "name": "EU AI Act – Article 5: Prohibited AI Practices",
            "short_name": "EU AI Act Art. 5",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2025, 2, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 5 – Prohibited AI Practices

The following AI practices are prohibited under the EU AI Act:

1. Placing on the market, putting into service or using an AI system that deploys subliminal techniques beyond a person's consciousness or purposefully manipulative or deceptive techniques with the objective of materially distorting the behaviour of a person or a group of persons, thereby causing or likely to cause significant harm.

2. Placing on the market, putting into service or using an AI system that exploits vulnerabilities of a specific group of persons due to their age, disability or a specific social or economic situation with the objective of materially distorting the behaviour of a person pertaining to that group in a manner that causes or is likely to cause that person or another person significant harm.

3. Placing on the market, putting into service or using AI systems for the evaluation or classification of natural persons or groups of persons over a certain period of time based on their social behaviour or known, inferred or predicted personal or personality characteristics, with the social score leading to either or both of the following: (a) detrimental or unfavourable treatment of certain natural persons or groups of persons in social contexts that are unrelated to the contexts in which the data was originally generated or collected; (b) detrimental or unfavourable treatment of certain natural persons or groups of persons that is unjustified or disproportionate to their social behaviour or its gravity.

4. The use of AI systems for real-time remote biometric identification systems in publicly accessible spaces for the purpose of law enforcement, unless strictly necessary (with limited exceptions for targeted search of victims, terrorism prevention, and prosecution of serious offences, subject to judicial authorisation).

5. AI systems that infer emotions of natural persons in the areas of workplace and education institutions, except for medical or safety reasons.

6. AI systems for biometric categorisation of natural persons based on biometric data to deduce or infer their race, political opinions, trade union membership, religious or philosophical beliefs, or sexual orientation.

7. Untargeted scraping of facial images from the internet or CCTV footage to create or expand facial recognition databases.

Compliance Requirements:
- Any AI system falling under these prohibitions must not be deployed or marketed in the EU.
- Organizations must audit their AI systems to confirm they do not employ any of these practices.
- Violations carry the highest penalties under the Act (up to €35 million or 7% of global annual turnover).
""",
        },
        {
            "name": "EU AI Act – Article 6: Classification Rules for High-Risk AI Systems",
            "short_name": "EU AI Act Art. 6",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 6 – Classification Rules for High-Risk AI Systems

1. Irrespective of whether an AI system is placed on the market or put into service independently from the products referred to in points (a) and (b) of this paragraph, that AI system shall be considered to be high-risk where both of the following conditions are fulfilled:
   (a) the AI system is intended to be used as a safety component of a product, or is itself a product, covered by the Union harmonisation legislation listed in Annex II;
   (b) the product whose safety component is the AI system, or the AI system itself as a product, is required to undergo a third-party conformity assessment with a view to the placing on the market or putting into service of that product pursuant to the Union harmonisation legislation listed in Annex II.

2. In addition to the high-risk AI systems referred to in paragraph 1, AI systems referred to in Annex III shall also be considered to be high-risk.

3. By derogation from paragraph 2, an AI system referred to in Annex III shall not be considered to be high-risk where it does not pose a significant risk of harm to the health, safety or fundamental rights of natural persons, including by not materially influencing the outcome of decision making. An AI system shall not be considered as posing a significant risk of harm where it performs a narrowly procedural task, is intended to improve the result of a previously completed human activity, is designed to detect decision-making patterns or deviations from prior decision-making patterns, or performs a preparatory task to an assessment relevant for the purposes of the use cases listed in Annex III.

Key High-Risk Categories (from Annex III):
- Biometric identification and categorisation systems
- Critical infrastructure management
- Educational and vocational training access systems
- Employment and workers management (hiring, promotion, task allocation)
- Access to essential services (credit scoring, insurance, social benefits)
- Law enforcement systems
- Migration, asylum and border control management
- Administration of justice and democratic processes

Compliance Requirements:
- Providers must determine if their AI system meets the classification criteria.
- High-risk systems require conformity assessment, technical documentation, and registration.
- Self-assessment is permitted for some high-risk systems; third-party assessment for others.
""",
        },
        {
            "name": "EU AI Act – Article 9: Risk Management System",
            "short_name": "EU AI Act Art. 9",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 9 – Risk Management System

1. A risk management system shall be established, implemented, documented and maintained in relation to high-risk AI systems.

2. The risk management system shall consist of a continuous iterative process run throughout the entire lifecycle of a high-risk AI system, requiring regular systematic review and updating. It shall comprise the following steps:
   (a) identification and analysis of the known and reasonably foreseeable risks that the high-risk AI system can pose to health, safety or fundamental rights when the high-risk AI system is used in accordance with its intended purpose;
   (b) estimation and evaluation of the risks that may emerge when the high-risk AI system is used in accordance with its intended purpose, and under conditions of reasonably foreseeable misuse;
   (c) evaluation of other possibly arising risks based on the analysis of data gathered from the post-market monitoring system;
   (d) adoption of appropriate and targeted risk management measures designed to address the risks identified pursuant to points (a), (b) and (c).

3. The risk management measures referred to in point (d) of paragraph 2 shall give due consideration to the effects and possible interactions resulting from the combined application of the requirements set out in Chapter 2. They shall take into account the generally acknowledged state of the art, including as reflected in relevant harmonised standards or common specifications.

4. The risk management measures referred to in point (d) of paragraph 2 shall be such that the residual risk associated with each hazard as well as the overall residual risk of the high-risk AI systems is judged to be acceptable. In identifying the most appropriate risk management measures, the following shall be ensured:
   (a) elimination or reduction of risks as far as technically possible through adequate design and development;
   (b) implementation of adequate mitigation and control measures in relation to risks that cannot be eliminated;
   (c) provision of adequate information pursuant to Articles 13 and 23 and, where appropriate, training to deployers.

5. High-risk AI systems shall be tested for the purposes of identifying the most appropriate and targeted risk management measures. Testing shall ensure that high-risk AI systems perform consistently for their intended purpose and they are in compliance with the requirements set out in this Chapter. The testing of the high-risk AI systems shall be performed, as appropriate, at any point in the development process, and, in any event, prior to placing on the market. Testing against prior defined metrics and probabilistic thresholds that are appropriate to the intended purpose of the high-risk AI system shall be conducted.

Compliance Requirements:
- Maintain documented risk management procedures throughout the AI lifecycle.
- Conduct risk identification, estimation, and evaluation before deployment.
- Implement residual risk mitigation measures.
- Perform pre-deployment testing with documented metrics.
- Establish post-market monitoring to update risk assessments.
""",
        },
        {
            "name": "EU AI Act – Article 10: Data and Data Governance",
            "short_name": "EU AI Act Art. 10",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 10 – Data and Data Governance

1. High-risk AI systems which make use of techniques involving the training of AI models with data shall be developed on the basis of training, validation and testing data sets that meet the quality criteria referred to in paragraphs 2 to 5 where such data sets are used.

2. Training, validation and testing data sets shall be subject to data governance and management practices. Those practices shall concern in particular:
   (a) the relevant design choices;
   (b) data collection processes and the origin of data, and in the case of personal data, the original purpose of the data collection;
   (c) relevant data preparation processing operations, such as annotation, labelling, cleaning, updating, enrichment and aggregation;
   (d) the formulation of assumptions, notably with respect to the information that the data is supposed to measure and represent;
   (e) an assessment of the availability, quantity and suitability of the data sets that are needed;
   (f) examination in view of possible biases that are likely to affect the health and safety of persons, have a negative impact on fundamental rights or lead to discrimination prohibited under Union law, especially when data outputs influence inputs for future operations;
   (g) appropriate measures to detect, prevent and mitigate possible biases;
   (h) the identification of any possible data gaps or shortcomings, and how those gaps and shortcomings can be addressed.

3. Training, validation and testing data sets shall be relevant, sufficiently representative, and to the best extent possible, free of errors and complete in view of the intended purpose. They shall have the appropriate statistical properties, including, where applicable, as regards the persons or groups of persons in relation to whom the high-risk AI system is intended to be used. These characteristics of the data sets may be met at the level of individual data sets or a combination thereof.

4. Data sets shall take into account, to the extent required by their intended purpose, the characteristics or elements that are particular to the specific geographical, contextual, behavioural or functional setting within which the high-risk AI system is intended to be used.

5. To the extent that it is strictly necessary for the purposes of ensuring bias detection and correction in relation to the high-risk AI systems in accordance with paragraph (2)(f) and (g) of this Article, the providers of such systems may exceptionally process special categories of personal data referred to in Article 9(1) of Regulation (EU) 2016/679.

Compliance Requirements:
- Establish data governance documentation for training/validation/testing datasets.
- Document data sources, collection processes, and preprocessing steps.
- Assess and mitigate bias in training data.
- Ensure data is representative of the target deployment population.
- Maintain records of data gaps and how they are addressed.
""",
        },
        {
            "name": "EU AI Act – Article 11: Technical Documentation",
            "short_name": "EU AI Act Art. 11",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 11 – Technical Documentation

1. The technical documentation of a high-risk AI system shall be drawn up before that system is placed on the market or put into service and shall be kept up to date. The technical documentation shall be drawn up in such a way as to demonstrate that the high-risk AI system complies with the requirements set out in this Chapter and provide national competent authorities and notified bodies with all the information necessary to assess the compliance of the AI system with those requirements.

The technical documentation shall contain, at a minimum, the elements set out in Annex IV (which includes):
   (a) a general description of the AI system, including its intended purpose, the persons responsible for developing the system, the date and version of the system;
   (b) a detailed description of the elements of the AI system and of the process for its development, including the methods and steps performed for the development and validation;
   (c) detailed information about the monitoring, functioning and control of the AI system;
   (d) a description of the appropriateness of the performance metrics for the specific AI system;
   (e) a description of any change made to the system through its lifecycle;
   (f) a list of the harmonised standards applied in full or in part;
   (g) a copy of the EU declaration of conformity;
   (h) a detailed description of the system in place to evaluate the AI system performance in the post-market phase.

2. Where a high-risk AI system related to products to which the Union harmonisation legislation listed in Annex II applies is placed on the market or put into service, a single set of technical documentation shall be drawn up containing all the information set out in paragraph 1 as well as the information required under those legal acts.

Compliance Requirements:
- Create and maintain technical documentation before deployment of high-risk AI systems.
- Include general description, development methodology, performance metrics, and monitoring plans.
- Keep documentation updated throughout the system lifecycle.
- Make documentation available to competent authorities on request.
- Align with Annex IV documentation requirements.
""",
        },
        {
            "name": "EU AI Act – Article 13: Transparency and Provision of Information to Deployers",
            "short_name": "EU AI Act Art. 13",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 13 – Transparency and Provision of Information to Deployers

1. High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent to enable deployers to interpret the system's output and use it appropriately. An appropriate type and degree of transparency shall be ensured with a view to achieving compliance with the relevant obligations of the provider and deployer set out in Chapter 3 of this Title.

2. High-risk AI systems shall be accompanied by instructions for use in an appropriate digital format or otherwise that include concise, complete, correct and clear information that is relevant, accessible and comprehensible to deployers.

3. The information referred to in paragraph 2 shall specify:
   (a) the identity and the contact details of the provider and, where applicable, of its authorised representative;
   (b) the characteristics, capabilities and limitations of performance of the high-risk AI system, including: (i) its intended purpose; (ii) the level of accuracy, robustness and cybersecurity referred to in Article 15 against which the high-risk AI system has been tested and validated and which can be expected, and any known and foreseeable circumstances that may have an impact on that expected level of accuracy, robustness and cybersecurity; (iii) any known or foreseeable circumstance, related to the use of the high-risk AI system in accordance with its intended purpose or under conditions of reasonably foreseeable misuse, which may lead to risks to the health and safety or fundamental rights; (iv) where applicable, the technical capabilities and characteristics of the high-risk AI system to provide information that is relevant to its explainability; (v) where applicable, its performance as regards the persons or groups of persons on whom the system is intended to be used;
   (c) the changes to the high-risk AI system and its performance which have been pre-determined by the provider at the moment of the initial conformity assessment, if any;
   (d) where applicable, a description of the human oversight measures;
   (e) the computational and hardware resources needed, the expected lifetime of the high-risk AI system and any necessary maintenance and care measures, including their frequency, to ensure the proper functioning of that AI system, including as regards software updates.

Compliance Requirements:
- Provide comprehensive instructions for use with high-risk AI systems.
- Document known limitations, performance levels, and foreseeable risks.
- Include information on human oversight mechanisms.
- Specify computational requirements and maintenance procedures.
- Ensure transparency enables deployers to interpret outputs appropriately.
""",
        },
        {
            "name": "EU AI Act – Article 14: Human Oversight",
            "short_name": "EU AI Act Art. 14",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 14 – Human Oversight

1. High-risk AI systems shall be designed and developed in such a way, including with appropriate human-machine interface tools, that they can be effectively overseen by natural persons during the period in which the AI system is in use.

2. Human oversight shall aim to prevent or minimise the risks to health, safety or fundamental rights that may emerge when a high-risk AI system is used in accordance with its intended purpose or under conditions of reasonably foreseeable misuse, in particular when such risks persist notwithstanding the application of other requirements set out in this Chapter.

3. The oversight measures shall be commensurate with the risks, level of autonomy and context of use of the high-risk AI system, and shall be ensured through one or both of the following types of built-in operational tools:
   (a) measures that allow the persons to whom the human oversight is assigned to: (i) fully understand the capacities and limitations of the high-risk AI system and be able to duly monitor its operation, so that signs of anomalies, dysfunctions and unexpected performance can be detected and addressed as soon as possible; (ii) remain aware of the possible tendency of automatically relying or over-relying on the output produced by a high-risk AI system ('automation bias'); (iii) correctly interpret the high-risk AI system's output, taking into account in particular the characteristics of the system and the interpretation tools and methods available; (iv) decide, in any particular situation, not to use the high-risk AI system or otherwise disregard, override or reverse the output of the high-risk AI system; (v) intervene on the operation of the high-risk AI system or interrupt the system through a 'stop' button or a similar procedure that allows the system to come to a halt in a safe state;
   (b) measures that allow the persons to whom the human oversight is assigned to: (i) appropriately interact with the high-risk AI system; (ii) interpret its output; (iii) have access to the information and resources needed to exercise oversight of its operation.

4. For high-risk AI systems referred to in Annex III, points 1 and 6, the measures referred to in paragraph 3 shall be such as to ensure that no action or decision is taken by the deployer on the basis of the identification resulting from the system unless that identification has been separately verified and confirmed by two natural persons with the relevant competence, expertise and authority.

Compliance Requirements:
- Design AI systems with human oversight capabilities built in.
- Enable human operators to understand, monitor, and intervene in AI decisions.
- Prevent automation bias through design and training.
- Provide override and stop mechanisms.
- For biometric and law enforcement systems, require two-person verification of AI outputs.
- Document oversight procedures in technical documentation.
""",
        },
        {
            "name": "EU AI Act – Article 15: Accuracy, Robustness, and Cybersecurity",
            "short_name": "EU AI Act Art. 15",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 15 – Accuracy, Robustness, and Cybersecurity

1. High-risk AI systems shall be designed and developed in such a way that they achieve an appropriate level of accuracy, robustness and cybersecurity, and they perform consistently in those respects throughout their lifecycle.

2. The levels of accuracy and the relevant accuracy metrics of high-risk AI systems shall be declared in the accompanying instructions of use.

3. High-risk AI systems shall be resilient to errors, faults or inconsistencies that may occur within the system or the environment in which the system operates, in particular due to their interaction with natural persons or other systems. The technical robustness of high-risk AI systems may be achieved through technical redundancy solutions, which may include backup or fail-safe plans.

4. High-risk AI systems that continue to learn after being placed on the market or put into service shall be developed in such a way to ensure that possibly unfair, biased or otherwise incorrect outputs influencing input for future operations are addressed with appropriate mitigation measures.

5. High-risk AI systems shall be resilient to attempts by unauthorised third parties to alter their use, outputs or performance by exploiting the system vulnerabilities. The technical solutions aimed at ensuring the cybersecurity of high-risk AI systems shall be appropriate to the relevant circumstances and the risks. The technical solutions to address AI specific vulnerabilities shall include, as appropriate, measures to prevent, detect, respond to, resolve and control for attacks trying to manipulate the training dataset ('data poisoning'), inputs designed to cause the model to make a mistake ('adversarial examples'), model theft attacks, or attacks exploiting vulnerabilities in the digital or physical infrastructure in which the AI system is deployed.

Compliance Requirements:
- Define and document accuracy metrics before deployment.
- Build resilience against errors and inconsistencies.
- Implement cybersecurity measures specific to AI vulnerabilities (data poisoning, adversarial attacks).
- Continuously monitor performance after deployment.
- Address feedback loops in continually learning systems.
""",
        },
        {
            "name": "EU AI Act – Article 26: Obligations of Deployers of High-Risk AI Systems",
            "short_name": "EU AI Act Art. 26",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 26 – Obligations of Deployers of High-Risk AI Systems

1. Deployers of high-risk AI systems shall take appropriate technical and organisational measures to ensure they use such systems in accordance with the instructions for use accompanying the systems.

2. Deployers shall assign the task of human oversight to natural persons who have the necessary competence, training and authority, and the necessary resources.

3. The obligations set out in paragraphs 1 and 2 are without prejudice to other deployer obligations under Union or national law and to the deployer's freedom to organise its own resources and activities for the purpose of implementing the human oversight measures indicated by the provider.

4. Without prejudice to paragraph 1, to the extent the deployer exercises control over the input data, that deployer shall ensure that input data is relevant and sufficiently representative in view of the intended purpose of the high-risk AI system.

5. Deployers shall monitor the operation of the high-risk AI system on the basis of the instructions for use and, where relevant, inform providers as referred to in Article 72(1). Where deployers have reason to consider that the use of the high-risk AI system in accordance with the instructions may result in the AI system presenting a risk within the meaning of Article 79(1), they shall immediately inform the provider or distributor and the relevant market surveillance authority, and shall suspend the use of the system.

6. Deployers of high-risk AI systems shall keep the logs automatically generated by that high-risk AI system, to the extent such logs are under their control, for a period that is appropriate to the intended purpose of the high-risk AI system, of at least 6 months, unless provided otherwise in applicable Union or national law.

7. Deployers of high-risk AI systems that are public authorities, or Union institutions, bodies, offices or agencies shall carry out a fundamental rights impact assessment prior to putting the high-risk AI system into service.

8. Deployers shall use the information provided under Article 13 to the degree possible to carry out a data protection impact assessment as required by Article 35 of Regulation (EU) 2016/679 or Article 27 of Directive (EU) 2016/680.

Compliance Requirements:
- Follow provider instructions for use.
- Assign qualified human oversight personnel.
- Monitor AI system operation and report anomalies.
- Retain AI system logs for minimum 6 months.
- Conduct fundamental rights impact assessment (public authorities).
- Ensure input data quality.
""",
        },
        {
            "name": "EU AI Act – Article 49: Registration Obligations",
            "short_name": "EU AI Act Art. 49",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 49 – Registration Obligations for Operators of High-Risk AI Systems

1. Before placing on the market or putting into service a high-risk AI system listed in Annex III, the provider of that system shall, or in the case of high-risk AI systems intended to be used by deployers who are public authorities, Union institutions, bodies, offices or agencies, the provider of that system shall ensure that the deployer of the system registers itself and the system in the EU database referred to in Article 71.

2. Before putting into service or using a high-risk AI system listed in Annex III, deployers of that system that are public authorities, Union institutions, bodies, offices or agencies shall register themselves and the system in the EU database referred to in Article 71.

3. For high-risk AI systems referred to in Annex III, point 2, placed on the market or put into service by providers that are credit institutions regulated by Directive 2013/36/EU, the registration shall be performed in the EU database referred to in Article 71 as part of the documentation maintained under Article 74 of that Directive.

4. For high-risk AI systems referred to in Annex III, point 4, the obligation for registration in the EU database referred to in Article 71 shall be suspended until the date of the first review of the list of high-risk AI systems set out in Annex III pursuant to Article 89.

The EU AI Act database entry must include:
- Provider name and contact information
- AI system description and intended purpose
- Status of the conformity assessment
- Summary of relevant post-market monitoring plan
- Declaration of conformity reference

Compliance Requirements:
- Register high-risk AI systems in the EU AI Act database before deployment.
- Public authority deployers must also register independently.
- Maintain accurate registration information throughout system lifecycle.
- Update registration on material changes to the system.
""",
        },
        {
            "name": "EU AI Act – Article 50: Transparency Obligations for Certain AI Systems",
            "short_name": "EU AI Act Art. 50",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 50 – Transparency Obligations for Providers and Users of Certain AI Systems

1. Providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system, unless this is obvious from the circumstances and the context of use. This obligation shall not apply to AI systems authorised by law to detect, prevent, investigate and prosecute criminal offences, subject to appropriate safeguards for the rights and freedoms of third parties.

2. Providers of AI systems, including general-purpose AI systems, generating synthetic audio, image, video or text content, shall ensure that the outputs of the AI system are marked in a machine-readable format and detectable as artificially generated or manipulated. Providers shall ensure their technical solutions are effective, interoperable, robust and reliable as far as this is technically feasible, taking into account the specificities and limitations of various types of content, the costs of implementation and the generally acknowledged state of the art, as may be reflected in relevant technical standards. This obligation shall not apply to the extent the AI systems perform an assistive function for standard editing or do not substantially alter the input data provided by the deployer or its semantics, or where authorised by law to detect, prevent, investigate and prosecute criminal offences.

3. Deployers of an emotion recognition system or a biometric categorisation system shall inform the natural persons exposed thereto of the operation of the system, and shall process the personal data in accordance with Regulation (EU) 2016/679, Regulation (EU) 2018/1725, and Directive (EU) 2016/680, as applicable.

4. Deployers who use an AI system to generate or manipulate image, audio or video content constituting a deep fake shall disclose that the content has been artificially generated or manipulated. This obligation shall not apply where the use is authorised by law to detect, prevent, investigate or prosecute criminal offences or it is necessary for the exercise of the right to freedom of expression and arts and sciences.

5. The information referred to in paragraphs 1 to 4 shall be provided to the natural persons concerned in a clear and distinguishable manner at the latest at the time of the first interaction or exposure.

Compliance Requirements:
- Disclose AI interaction to users (chatbots, virtual assistants).
- Mark AI-generated content in machine-readable format.
- Inform subjects of emotion recognition and biometric categorisation systems.
- Label deep fake content as artificially generated.
- Provide disclosures clearly and at first interaction.
""",
        },
        {
            "name": "EU AI Act – Article 52: Transparency Obligations (General Purpose)",
            "short_name": "EU AI Act Art. 52",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2025, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 52 – Transparency Obligations for General-Purpose AI Systems

General-purpose AI (GPAI) model providers must meet specific transparency requirements under the EU AI Act.

1. Providers of general-purpose AI models shall draw up and keep up to date technical documentation of the model, including its training, testing process and the results of its evaluation, which shall contain, at a minimum, the elements set out in Annex XI.

2. Providers of general-purpose AI models shall draw up, keep up to date and make available information and documentation to providers of AI systems who intend to integrate the general-purpose AI model into their AI systems. This information shall enable providers of AI systems to have a good understanding of the capabilities and limitations of the general-purpose AI model and to comply with their obligations pursuant to this Regulation.

3. Providers of general-purpose AI models shall put in place a policy to comply with Union law on copyright and related rights, and in particular to identify and comply with, including through state of the art technologies, a reservation of rights expressed pursuant to Article 4(3) of Directive (EU) 2019/790.

4. Providers of general-purpose AI models shall publish a sufficiently detailed summary about the content used for training of the general-purpose AI model, according to a template provided by the AI Office.

For GPAI models with systemic risk (as defined by the Act):
- Perform adversarial testing (red-teaming)
- Report serious incidents to the AI Office
- Implement cybersecurity measures
- Assess and mitigate systemic risks

Compliance Requirements:
- Provide technical documentation per Annex XI.
- Publish training data summary.
- Establish copyright compliance policy.
- For systemic risk models: adversarial testing, incident reporting, cybersecurity measures.
""",
        },
        {
            "name": "EU AI Act – Article 62: Reporting of Serious Incidents",
            "short_name": "EU AI Act Art. 62",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Article 62 – Reporting of Serious Incidents

1. Providers of high-risk AI systems placed on the Union market shall report any serious incident to the market surveillance authorities of the Member States where that incident occurred.

2. The report referred to in paragraph 1 shall be made immediately after the provider has established a causal link between the AI system and the serious incident or the reasonable likelihood of such a link, and, in any event, not later than 15 days after the providers becomes aware of the serious incident.

3. Notwithstanding paragraph 2, in the event of a widespread serious incident, the notification shall be provided immediately, and not later than 2 days after the provider becomes aware of that incident.

4. Notwithstanding paragraph 2, in the event of the death of a person, the notification shall be provided immediately after the provider has established or as soon as it suspects a causal link between the high-risk AI system and the serious incident, and in any event not later than 10 days after the date on which the provider becomes aware of the serious incident.

A 'serious incident' means an incident or malfunctioning of an AI system that directly or indirectly leads to:
   (a) the death of a person or serious damage to a person's health;
   (b) a serious and irreversible disruption of the management or operation of critical infrastructure;
   (c) infringement of obligations under Union law intended to protect fundamental rights;
   (d) serious damage to property or the environment.

Compliance Requirements:
- Establish incident detection and reporting procedures.
- Report serious incidents within 15 days (standard), 2 days (widespread), 10 days (death).
- Identify causal links between AI system behavior and incidents.
- Maintain incident logs and post-incident reports.
- Cooperate with market surveillance authorities.
""",
        },
        {
            "name": "EU AI Act – Article 71 & 99: Fines and Sanctions",
            "short_name": "EU AI Act Art. 71/99",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2025, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Articles 71 and 99 – Fines and Sanctions

Article 71 – Penalties:

1. Non-compliance with the prohibition of the AI practices referred to in Article 5:
   - Administrative fines up to €35,000,000 or, if the offender is an undertaking, up to 7% of its total worldwide annual turnover for the preceding financial year, whichever is higher.

2. Non-compliance of the AI system or the general-purpose AI model with any requirements or obligations under this Regulation, other than those referred to in Article 5:
   - Administrative fines up to €15,000,000 or, if the offender is an undertaking, up to 3% of its total worldwide annual turnover for the preceding financial year, whichever is higher.

3. The supply of incorrect, incomplete or misleading information to notified bodies and national competent authorities in reply to a request:
   - Administrative fines up to €7,500,000 or, if the offender is an undertaking, up to 1% of its total worldwide annual turnover for the preceding financial year, whichever is higher.

Article 99 – Penalties for Member States applies equivalent rules to SMEs and start-ups with proportionate fines.

Key factors in determining fine amounts:
- Nature, gravity, and duration of the infringement
- Whether the infringement was intentional or negligent
- Any actions taken to mitigate harm
- Degree of cooperation with authorities
- Financial benefits gained from the infringement

Compliance Requirements:
- Understand penalty tiers and maximum fines applicable to your organization size.
- Implement compliance program to avoid highest-tier penalties (prohibited practices).
- Cooperate fully with regulatory authorities to benefit from fine reductions.
- Report incidents proactively and accurately.
""",
        },
        {
            "name": "EU AI Act – Annex I: AI Techniques and Approaches",
            "short_name": "EU AI Act Annex I",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2025, 2, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Annex I – List of AI Techniques and Approaches (Definition of AI Systems)

For the purposes of this Regulation, 'artificial intelligence system' (AI system) means a machine-based system that is designed to operate with varying levels of autonomy and that may exhibit adaptiveness after deployment, and that, for explicit or implicit objectives, infers, from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions that can influence physical or virtual environments.

AI approaches covered under this Regulation include:
1. Machine learning approaches, including supervised, unsupervised, and reinforcement learning, using a wide variety of methods including deep learning.

2. Logic and knowledge-based approaches, including knowledge representation, inductive (logic) programming, knowledge bases, inference and deductive engines, (symbolic) reasoning, and expert systems.

3. Statistical approaches, Bayesian estimation, search and optimization methods.

Systems that fall WITHIN scope (AI systems):
- Systems that learn from data (supervised ML, unsupervised ML, deep learning)
- Systems that reason based on predefined rules and knowledge bases
- Systems using statistical inference to make predictions or recommendations

Systems that may fall OUTSIDE scope (traditional software):
- Simple rule-based systems executing predetermined operations
- Classical algorithms that do not infer or learn
- Search engines (unless using learning components)

Compliance Requirements:
- Determine whether your system qualifies as an AI system under Annex I.
- Document the AI techniques used in technical documentation.
- Systems using techniques outside this annex may not be subject to AI Act requirements.
- Hybrid systems combining AI and non-AI components must assess each AI component individually.
""",
        },
        {
            "name": "EU AI Act – Annex II: Union Harmonisation Legislation",
            "short_name": "EU AI Act Annex II",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Annex II – List of Union Harmonisation Legislation

AI systems used as safety components in products or as products themselves that are subject to third-party conformity assessment under the following Union harmonisation legislation are automatically classified as high-risk:

Section A (Union harmonisation legislation with conformity assessment involving a third-party body):
1. Regulation (EU) 2016/425 on personal protective equipment
2. Regulation (EU) 2016/426 on appliances burning gaseous fuels
3. Regulation (EU) 2017/745 on medical devices
4. Regulation (EU) 2017/746 on in vitro diagnostic medical devices
5. Regulation (EU) 2018/858 on approval of motor vehicles and their trailers
6. Regulation (EU) 2018/1139 on common rules in the field of civil aviation
7. Regulation (EU) 2019/2144 on type-approval requirements for motor vehicles
8. Directive 2014/90/EU on marine equipment
9. Directive (EU) 2016/797 on the interoperability of the rail system within the EU

Section B (Union harmonisation legislation with self-assessment):
10. Regulation (EU) No 305/2011 on construction products
11. Directive 2009/48/EC on the safety of toys
12. Directive 2011/65/EU on restriction of hazardous substances in electrical/electronic equipment
13. Directive 2013/29/EU on pyrotechnic articles
14. Directive 2014/31/EU on non-automatic weighing instruments
15. Directive 2014/32/EU on measuring instruments
16. Regulation (EU) 2023/1230 on machinery

Compliance Requirements:
- Check whether your AI system is used within any product category listed in Annex II.
- If yes, the AI system is automatically classified as high-risk regardless of Annex III.
- Third-party conformity assessment is mandatory for Section A products.
- Self-assessment is available for Section B products.
- Document which harmonisation legislation applies to your AI system.
""",
        },
        {
            "name": "EU AI Act – Annex III: High-Risk AI System Categories",
            "short_name": "EU AI Act Annex III",
            "jurisdiction": "EU",
            "effective_date": datetime(2024, 8, 1),
            "enforcement_date": datetime(2026, 8, 2),
            "category": "AI Governance",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            "full_text": """Annex III – High-Risk AI Systems Referred to in Article 6(2)

The following AI systems are classified as high-risk:

1. BIOMETRIC SYSTEMS
   1(a) AI systems intended to be used for biometric identification of natural persons (remote biometric identification)
   1(b) AI systems intended to be used for biometric categorisation of natural persons based on sensitive attributes (race, political opinions, religious beliefs, health data, sexual orientation)
   1(c) AI systems for emotion recognition

2. CRITICAL INFRASTRUCTURE
   AI systems intended to be used as safety components in the management and operation of: road traffic, supply of water, gas, heating, electricity.

3. EDUCATION AND VOCATIONAL TRAINING
   AI systems used to: determine access to, or admission to, educational institutions; evaluate learning outcomes; assess students; detect prohibited behaviour.

4. EMPLOYMENT, WORKERS MANAGEMENT, AND ACCESS TO SELF-EMPLOYMENT
   AI systems used to: recruit/screen job applicants (CV screening, interview assessment); make decisions on promotion/termination; allocate tasks; monitor and evaluate performance.

5. ACCESS TO ESSENTIAL PRIVATE SERVICES AND ESSENTIAL PUBLIC SERVICES AND BENEFITS
   5(a) AI used in creditworthiness assessment and credit scoring for retail clients
   5(b) AI used in life and health insurance risk assessment and pricing
   5(c) AI used in evaluating individuals for public assistance benefits
   5(d) AI used in emergency services (calls classification, prioritisation of police, firefighters, medical aid)

6. LAW ENFORCEMENT
   AI used by law enforcement authorities for: individual risk assessment; polygraph-like tools; evaluation of evidence reliability; crime analytics (geographic or behavioral prediction); profiling in criminal investigations; facial recognition in criminal investigations.

7. MIGRATION, ASYLUM AND BORDER CONTROL MANAGEMENT
   AI used for: risk assessment of persons applying for asylum/visa/permit; polygraph-like tools; examination of asylum/visa/permit applications; detection of undeclared goods; border surveillance.

8. ADMINISTRATION OF JUSTICE AND DEMOCRATIC PROCESSES
   AI used by judicial authorities to: research and interpret facts and law; apply law to a concrete set of facts.

Compliance Requirements:
- Map your AI system's use case against each category above.
- If your system falls in any category, high-risk obligations apply (Articles 9-15, 17, 26, 49).
- Document the Annex III category applicable to your system.
- Consider whether the Article 6(3) exception (non-significant risk) applies.
""",
        },
    ]


def _us_regulations() -> List[dict]:
    return [
        {
            "name": "New York City Local Law 144 – Automated Employment Decision Tools",
            "short_name": "NYC LL144",
            "jurisdiction": "US-NYC",
            "effective_date": datetime(2023, 1, 1),
            "enforcement_date": datetime(2023, 7, 5),
            "category": "AI Employment",
            "url": "https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page",
            "full_text": """New York City Local Law 144 – Automated Employment Decision Tools (AEDT)

Overview:
NYC Local Law 144 (effective January 1, 2023, enforced from July 5, 2023) requires employers and employment agencies that use automated employment decision tools (AEDTs) in hiring or promotion decisions affecting NYC-based workers to:

Key Requirements:

1. BIAS AUDIT
   - Must conduct an independent bias audit of the AEDT before use
   - Audit must be performed annually
   - Audit must assess disparate impact of the tool on sex, race/ethnicity, and intersectional categories
   - Must calculate impact ratios for each category using 4/5ths (80%) rule or statistical significance
   - The bias audit must be conducted by an independent auditor (not affiliated with the employer or AEDT developer)

2. PUBLIC NOTICE OF AUDIT RESULTS
   - Employers must publish a summary of bias audit results on their website at least 10 business days before the AEDT is used
   - Summary must include: date of audit, name of independent auditor, demographic categories tested, results of the audit (impact ratios)

3. CANDIDATE NOTIFICATION
   - Employers must notify candidates in the job posting or 10 business days before the AEDT is used that an AEDT will be used
   - Must notify candidates that they may request an alternative selection process or accommodation
   - Must provide candidates with information about the type of data collected and how it will be used

4. DATA RETENTION AND DISCLOSURE
   - AEDT data used in employment decisions must be retained for at least 4 years
   - On request, employers must disclose the job qualifications and characteristics the AEDT uses

Definitions:
- AEDT: Any computational process derived from machine learning, statistical modeling, data analytics, or AI that issues simplified output used to substantially assist or replace discretionary decision-making in employment decisions
- Substantially assist or replace: Relies solely on a simplified output; uses a simplified output as one of a set of criteria where the output is weighted more than others; or uses a simplified output to overrule conclusions derived from other factors

Penalties:
- Civil penalties: $375–$1,500 per violation per day
- City agencies may seek injunctive relief

Compliance Checklist:
☐ Determine if tools used in NYC hiring/promotion qualify as AEDTs
☐ Commission independent bias audit annually
☐ Post audit summary publicly before using AEDT
☐ Include AEDT notification in job postings
☐ Establish data retention for 4+ years
☐ Provide accommodation/alternative process option to candidates
""",
        },
        {
            "name": "Colorado Artificial Intelligence Act (SB24-205)",
            "short_name": "Colorado SB205",
            "jurisdiction": "US-CO",
            "effective_date": datetime(2024, 5, 17),
            "enforcement_date": datetime(2026, 2, 1),
            "category": "AI Governance",
            "url": "https://leg.colorado.gov/bills/sb24-205",
            "full_text": """Colorado Artificial Intelligence Act – SB 24-205

Overview:
The Colorado AI Act (signed May 17, 2024, effective February 1, 2026) is the first comprehensive state AI law in the United States. It regulates "high-risk AI systems" used in "consequential decisions" affecting Colorado residents.

Key Definitions:
- High-risk AI system: Any AI system used in making consequential decisions in employment, education, financial/lending services, healthcare (clinical assessment), housing, insurance, and legal services.
- Consequential decision: A decision that has a material, legal, or significant effect on a Colorado consumer's access to employment, education, financial services, healthcare, housing, insurance, or legal services.
- Developer: Entity that develops or substantially modifies a high-risk AI system for deployment.
- Deployer: Entity that deploys a high-risk AI system.

DEVELOPER OBLIGATIONS:
1. Use reasonable care to protect consumers from algorithmic discrimination
2. Make available documentation to deployers:
   - Intended uses and known limitations
   - Steps taken to mitigate known or reasonably foreseeable risks
   - Performance metrics across demographic groups
   - Data governance policies
   - Instructions for deployers to meet their obligations
3. Provide notice to deployers if the developer becomes aware of algorithmic discrimination
4. Make a publicly accessible statement of high-risk AI systems developed/modified and how algorithmic discrimination risks are managed

DEPLOYER OBLIGATIONS:
1. Use reasonable care to protect consumers from algorithmic discrimination
2. Implement a risk management program (aligned with NIST AI Risk Management Framework)
3. Conduct annual reviews of high-risk AI systems
4. Notify consumers:
   - That a high-risk AI system was used in making a consequential decision
   - Of the nature of the consequential decision
   - Of any adverse decision
5. Provide consumers the ability to correct inaccurate personal data
6. Provide consumers the right to appeal automated decisions
7. Disclose to the AG how high-risk AI systems are used and managed (if requested)

EXEMPTIONS:
- Small businesses (< 50 employees) that are sole deployers and not developers have limited obligations
- Testing environments
- Open-source systems where developer cannot control deployment

ALGORITHMIC DISCRIMINATION DEFINITION:
Any condition in which the use of a high-risk artificial intelligence system results in unlawful differential treatment or impact that disfavors an individual or group of individuals on the basis of race, color, ethnicity, sex, sexual orientation, gender identity, religion, age, national origin, disability, veteran status, or genetic information.

ENFORCEMENT:
- Attorney General exclusive enforcement
- Civil penalties: up to $20,000 per violation
- 60-day cure period for first violations

Compliance Checklist:
☐ Determine if AI systems are used in consequential decisions for Colorado residents
☐ Implement NIST AI RMF-aligned risk management program
☐ Conduct annual reviews and impact assessments
☐ Establish consumer notification procedures
☐ Build appeal and data correction mechanisms
☐ Document all high-risk AI systems and publish statement
""",
        },
        {
            "name": "FTC AI Guidelines – Artificial Intelligence and Algorithmic Accountability",
            "short_name": "FTC AI Guidelines",
            "jurisdiction": "US-Federal",
            "effective_date": datetime(2021, 4, 19),
            "enforcement_date": datetime(2021, 4, 19),
            "category": "AI Consumer Protection",
            "url": "https://www.ftc.gov/business-guidance/blog/2021/04/aiming-truth-fairness-equity-your-companys-use-ai",
            "full_text": """FTC AI Guidelines – Aiming for Truth, Fairness, and Equity in AI

Overview:
The Federal Trade Commission (FTC) has issued guidance on AI and algorithmic systems under existing Section 5 authority (prohibiting unfair or deceptive acts/practices) and various consumer protection statutes. Key guidance published April 19, 2021 and updated in subsequent reports.

KEY FTC PRINCIPLES FOR AI:

1. TRUTHFULNESS AND NON-DECEPTION
   - Do not make false or unsubstantiated claims about AI capabilities.
   - Clearly disclose when consumers are interacting with AI (vs. humans).
   - Do not use dark patterns or manipulative design in AI systems.
   - Ensure marketing claims about AI accuracy or effectiveness are substantiated.

2. FAIRNESS AND NON-DISCRIMINATION
   - AI systems must not produce outputs that are discriminatory or biased.
   - Consider impact on protected classes in AI design and deployment.
   - Validate AI systems for disparate impact across demographic groups.
   - Apply the Equal Credit Opportunity Act (ECOA) in credit/financial AI systems.

3. PRIVACY AND DATA MINIMIZATION
   - Collect only the data necessary for the AI system's function.
   - Provide clear notice and choice about data collection for AI training.
   - Comply with existing privacy frameworks (COPPA, FCRA, GLBA).
   - Avoid "surveillance business models" built on extensive data collection.

4. TRANSPARENCY AND EXPLAINABILITY
   - Provide meaningful explanations for AI decisions affecting consumers.
   - Adverse action notices must include meaningful AI decision explanations.
   - Do not obscure how AI systems work or their limitations.
   - Consider algorithmic impact assessments.

5. ROBUST AND EMPIRICALLY SOUND
   - Test AI systems before deployment to ensure they perform as claimed.
   - Monitor AI systems post-deployment for accuracy and bias.
   - Address known flaws or biases in AI systems promptly.
   - Maintain adequate safeguards against manipulation or adversarial attacks.

FTC ENFORCEMENT AUTHORITY:
- Section 5 FTC Act: Prohibits unfair or deceptive acts/practices
- FCRA: Consumer reporting AI applications
- ECOA: Credit decision AI
- COPPA: AI systems collecting children's data
- Civil penalties and consent decrees may be imposed

RELEVANT FTC ACTIONS:
- Scrutiny of AI "bias washing" (claiming AI is fair without adequate testing)
- Actions against companies making unsubstantiated AI claims
- Required algorithmic disgorgement as a remedy for AI trained on unlawfully collected data

Compliance Checklist:
☐ Substantiate all AI performance and accuracy claims
☐ Test for discriminatory bias before deployment
☐ Provide adverse action explanations for AI-driven decisions
☐ Implement data minimization practices
☐ Monitor AI systems post-deployment for bias and accuracy drift
☐ Maintain consumer notice and choice mechanisms
""",
        },
        {
            "name": "EEOC AI Guidance – Artificial Intelligence and Employment Discrimination",
            "short_name": "EEOC AI Guidance",
            "jurisdiction": "US-Federal",
            "effective_date": datetime(2023, 5, 18),
            "enforcement_date": datetime(2023, 5, 18),
            "category": "AI Employment",
            "url": "https://www.eeoc.gov/laws/guidance/questions-and-answers-clarify-and-provide-common-interpretation-uniform-guidelines",
            "full_text": """EEOC AI Guidance – Use of Artificial Intelligence in Employment Decisions

Overview:
The Equal Employment Opportunity Commission (EEOC) issued guidance in May 2023 on employer use of AI in employment decisions, clarifying that existing EEO laws apply to AI-assisted hiring and employment tools.

KEY PRINCIPLES:

1. TITLE VII AND AI DISPARATE IMPACT
   - Employers may be liable under Title VII for AI tools that create disparate impact on protected groups.
   - The "four-fifths rule" applies: if a selection rate for any race, sex, or ethnic group is less than 4/5 (80%) of the rate for the group with the highest selection rate, it is evidence of adverse impact.
   - Employers cannot avoid liability simply because the algorithm was developed by a vendor – the employer is responsible for the tool they use.
   - An employer relying on an AI hiring tool that disproportionately screens out individuals of a particular race or sex may violate Title VII.

2. ADA AND AI DISABILITY DISCRIMINATION
   - AI systems that assess qualifications, game-based assessments, or predictive tools may inadvertently screen out individuals with disabilities.
   - Employers must provide reasonable accommodation requests, including alternative non-AI assessment options.
   - Employers must keep medical information gathered by AI systems confidential.
   - AI that relies on game-based assessments may disadvantage people with cognitive, sensory, or other disabilities.

3. ADEA AND AGE DISCRIMINATION
   - AI systems trained on historical employment data may replicate age-based biases.
   - Tools that systematically rate younger workers higher based on proxy variables may violate the ADEA.
   - Employers should test AI employment tools for age-based disparate impact.

4. VENDOR LIABILITY FRAMEWORK
   - Employers remain responsible for discrimination caused by vendor-provided AI tools.
   - Audit vendor AI tools for potential bias and disparate impact.
   - Require indemnification clauses and bias testing documentation from AI vendors.
   - Ensure vendors provide transparency about data sources and validation methodology.

5. RECOMMENDED PRACTICES
   - Conduct regular audits of AI employment tools for adverse impact.
   - Maintain records of the AI tool's validation studies and statistical analyses.
   - Train HR staff on AI limitations and potential for bias.
   - Establish clear procedures for accommodation requests related to AI assessments.
   - Consider the full range of employment decisions where AI is used (screening, interview, promotion, performance, termination).

Compliance Checklist:
☐ Identify all AI tools used in employment decisions
☐ Conduct adverse impact analysis before deployment and annually
☐ Establish accommodation/alternative process for candidates
☐ Train HR on AI limitations
☐ Include bias testing requirements in vendor contracts
☐ Maintain records of AI validation studies
☐ Conduct disparate impact analysis for age, race, sex, disability
""",
        },
    ]


def _gdpr_regulations() -> List[dict]:
    return [
        {
            "name": "GDPR Article 6 – Lawfulness of Processing",
            "short_name": "GDPR Art. 6",
            "jurisdiction": "EU",
            "effective_date": datetime(2018, 5, 25),
            "enforcement_date": datetime(2018, 5, 25),
            "category": "Data Privacy",
            "url": "https://gdpr-info.eu/art-6-gdpr/",
            "full_text": """GDPR Article 6 – Lawfulness of Processing

Processing of personal data used in AI systems must have a valid legal basis. Processing is lawful only if and to the extent that at least one of the following applies:

1. CONSENT (Article 6(1)(a))
   - Data subject has given clear, specific, informed, and unambiguous consent.
   - For AI systems: consent must be meaningful given the context of automated processing.
   - Consent must be freely withdrawable and withdrawal must be easy.
   - Legitimate interest cannot override data subject rights for high-impact automated decisions.

2. CONTRACT (Article 6(1)(b))
   - Processing necessary for the performance of a contract with the data subject.
   - AI processing for contract fulfilment (e.g., fraud detection in payment processing) may qualify.
   - Must be strictly necessary, not merely convenient.

3. LEGAL OBLIGATION (Article 6(1)(c))
   - Processing required by EU or Member State law.
   - AI systems used in compliance monitoring, KYC, anti-money laundering may qualify.

4. VITAL INTERESTS (Article 6(1)(d))
   - Processing necessary to protect life of the data subject or another person.
   - Limited applicability for most AI use cases (emergency/medical situations only).

5. PUBLIC TASK (Article 6(1)(e))
   - Processing necessary for a task carried out in the public interest or in exercise of official authority.
   - Applies to government AI systems (law enforcement, social benefit assessment).

6. LEGITIMATE INTERESTS (Article 6(1)(f))
   - Requires balancing test: legitimate interest vs. rights/freedoms of data subject.
   - Cannot be used to override data subject rights where interests are overridden.
   - Not available to public authorities when processing in exercise of their tasks.
   - For AI systems: must consider the nature and purpose of the processing, the context, and expectations of data subjects.

For AI Training Data:
- Purpose limitation principle: data collected for one purpose cannot be freely reused for AI training.
- Compatibility test applies if data is repurposed for AI training.
- Anonymization or pseudonymization of training data reduces but does not eliminate obligations.

Compliance Requirements:
- Document the legal basis for each data processing activity in AI systems.
- Maintain Records of Processing Activities (RoPA) per Article 30.
- Ensure purpose limitation when repurposing data for AI training.
- Assess whether legitimate interest balancing test applies.
""",
        },
        {
            "name": "GDPR Article 9 – Processing of Special Categories of Personal Data",
            "short_name": "GDPR Art. 9",
            "jurisdiction": "EU",
            "effective_date": datetime(2018, 5, 25),
            "enforcement_date": datetime(2018, 5, 25),
            "category": "Data Privacy",
            "url": "https://gdpr-info.eu/art-9-gdpr/",
            "full_text": """GDPR Article 9 – Processing of Special Categories of Personal Data

Processing of special categories of personal data is prohibited unless an explicit exception applies. AI systems using sensitive data must comply with heightened requirements.

SPECIAL CATEGORIES:
- Racial or ethnic origin
- Political opinions
- Religious or philosophical beliefs
- Trade union membership
- Genetic data
- Biometric data processed to uniquely identify a natural person
- Health data
- Sex life or sexual orientation

RELEVANCE TO AI:
- AI systems trained on images may process biometric data
- AI health diagnostics process health data
- Sentiment analysis may infer political or religious beliefs
- Voice analysis may reveal health conditions
- Resume screening may involve ethnic origin inference

LAWFUL BASIS FOR PROCESSING SPECIAL CATEGORIES (Article 9(2)):
- Explicit consent (higher standard than Article 6 consent)
- Employment, social security and social protection law obligations
- Vital interests (and subject is incapable of giving consent)
- Processing by non-profit bodies with political, philosophical, religious, or trade-union aims
- Data manifestly made public by the data subject
- Legal claims
- Substantial public interest (with proportionality)
- Preventive/occupational medicine, medical diagnosis, healthcare
- Public health interests
- Archiving, scientific/historical research, statistics (with proportionality)

AI SYSTEM OBLIGATIONS:
- Identify whether AI system processes or infers special category data.
- Apply heightened security measures (encryption, access controls, pseudonymization).
- Conduct Data Protection Impact Assessment (DPIA) under Article 35.
- Limit special category data processing to the minimum necessary.
- Special consideration for biometric identification systems, health AI, and emotion recognition.

Compliance Requirements:
- Audit all AI systems for use of special category data (direct or inferred).
- Establish explicit legal basis for special category processing.
- Implement enhanced security measures for special category data in AI.
- Complete DPIA before deploying AI systems processing special categories.
""",
        },
        {
            "name": "GDPR Articles 13 & 14 – Transparency and Information Obligations",
            "short_name": "GDPR Art. 13/14",
            "jurisdiction": "EU",
            "effective_date": datetime(2018, 5, 25),
            "enforcement_date": datetime(2018, 5, 25),
            "category": "Data Privacy",
            "url": "https://gdpr-info.eu/art-13-gdpr/",
            "full_text": """GDPR Articles 13 and 14 – Transparency and Information Obligations for AI Systems

Data subjects must be informed about how their data is used in AI systems. Privacy notices must cover AI-specific processing.

ARTICLE 13 (Data Collected Directly from Subject) REQUIRES:
1. Identity and contact details of the data controller
2. Contact details of data protection officer (if applicable)
3. Purposes and legal basis of processing
4. Legitimate interests pursued (if Art. 6(1)(f) basis)
5. Recipients or categories of recipients
6. Transfers to third countries (adequacy decision, safeguards)
7. Retention period
8. Rights of data subjects (access, rectification, erasure, restriction, portability, objection)
9. Right to withdraw consent
10. Right to lodge a complaint with supervisory authority
11. Whether provision of personal data is statutory/contractual requirement
12. Existence of automated decision-making, including profiling, meaningful information about the logic involved, and the significance and consequences for the data subject

ARTICLE 14 (Data Not Obtained from Subject) ADDITIONALLY REQUIRES:
- The categories of personal data concerned
- Source of the personal data (including public sources)
- Must be provided within reasonable period (at most 1 month)

AI-SPECIFIC TRANSPARENCY REQUIREMENTS:
- Disclose existence of automated decision-making and profiling
- Provide meaningful information about the logic of automated decisions
- Explain significance and consequences of automated processing
- Include in privacy notice: what AI does, what data it uses, how it affects the subject

AI Training Data Transparency:
- Individuals whose data is used for AI training must be informed
- Must disclose that data may be used for ML/AI model training
- Must allow opt-out from training data use where legally possible

Compliance Requirements:
- Update privacy notices to include AI-specific disclosures.
- Explain automated decision-making logic in accessible terms.
- Inform data subjects if their data is used for AI training.
- Provide clear information on profiling activities.
- Ensure notices are layered (summary + detailed) for AI complexity.
""",
        },
        {
            "name": "GDPR Article 22 – Automated Individual Decision-Making Including Profiling",
            "short_name": "GDPR Art. 22",
            "jurisdiction": "EU",
            "effective_date": datetime(2018, 5, 25),
            "enforcement_date": datetime(2018, 5, 25),
            "category": "Data Privacy",
            "url": "https://gdpr-info.eu/art-22-gdpr/",
            "full_text": """GDPR Article 22 – Automated Individual Decision-Making, Including Profiling

This is the most directly AI-relevant article in the GDPR. It creates rights against purely automated decisions that significantly affect individuals.

SCOPE:
- Applies to any decision based solely on automated processing (including profiling)
- Produces legal or similarly significant effects on individuals
- Examples: automated credit scoring, automated job screening, automated benefit determination

GENERAL PROHIBITION:
Data subjects have the right not to be subject to decisions based solely on automated processing, including profiling, which produces legal effects or similarly significant effects.

EXCEPTIONS ALLOWING AUTOMATED DECISIONS (Article 22(2)):
1. Necessary for entering into or performance of a contract between controller and data subject
2. Authorised by Union or Member State law (with suitable measures to safeguard rights)
3. Based on explicit consent of the data subject

WHERE EXCEPTIONS APPLY, CONTROLLERS MUST:
- Implement suitable measures to safeguard the data subject's rights, freedoms, and legitimate interests
- At minimum: right to obtain human intervention; to express their point of view; to contest the decision
- Not use special categories of data (Article 9) unless explicit consent or substantial public interest grounds exist

HUMAN REVIEW REQUIREMENTS:
- Must allow human review of automated decisions on request
- Human reviewer must have actual authority and competence to reverse the automated decision
- Cannot be a "rubber stamp" review

PROFILING DEFINITION:
Any form of automated processing of personal data consisting of the use of personal data to evaluate certain personal aspects relating to a natural person, in particular to analyse or predict aspects concerning health, personal preferences, interests, reliability, behaviour, location, or movements.

AI SYSTEM IMPLICATIONS:
- Credit scoring AI: highly regulated, must allow human review
- Hiring AI: must provide meaningful human review if used as sole basis
- Insurance pricing AI: must comply with Article 22 if producing legal effects
- Healthcare diagnostic AI: may require human oversight mechanism

Compliance Requirements:
- Identify all automated decisions that produce legal or significant effects.
- Establish human review mechanisms for automated decisions.
- Provide explicit consent or contractual/legal basis for automated decisions.
- Do not use special category data in automated decisions without explicit consent.
- Document the logic of automated decision-making processes.
- Provide data subjects with right to contest automated decisions.
""",
        },
        {
            "name": "GDPR Article 35 – Data Protection Impact Assessment (DPIA)",
            "short_name": "GDPR Art. 35",
            "jurisdiction": "EU",
            "effective_date": datetime(2018, 5, 25),
            "enforcement_date": datetime(2018, 5, 25),
            "category": "Data Privacy",
            "url": "https://gdpr-info.eu/art-35-gdpr/",
            "full_text": """GDPR Article 35 – Data Protection Impact Assessment (DPIA) for AI Systems

A DPIA is mandatory when processing is "likely to result in a high risk to the rights and freedoms of natural persons." AI systems frequently trigger this requirement.

WHEN DPIA IS MANDATORY:
1. Systematic and extensive evaluation of personal aspects based on automated processing (including profiling) with decisions producing legal or similarly significant effects
2. Processing on a large scale of special categories of data (Article 9) or data relating to criminal convictions
3. Systematic monitoring of publicly accessible areas on a large scale

AI SYSTEMS THAT TYPICALLY REQUIRE A DPIA:
- AI used for employee monitoring/performance evaluation
- AI used in credit, insurance, or employment decisions
- AI processing biometric data (facial recognition, voice recognition)
- AI used in healthcare (patient outcome prediction, diagnostic AI)
- AI emotion recognition or behavioral profiling
- AI training using large datasets of personal data
- AI in smart city applications with surveillance capabilities

DPIA CONTENT REQUIREMENTS (Article 35(7)):
(a) Systematic description of the processing operations and purposes, including legitimate interests
(b) Assessment of necessity and proportionality of processing in relation to purposes
(c) Assessment of risks to rights and freedoms of data subjects
(d) Measures envisaged to address risks, including safeguards, security measures, and mechanisms to ensure protection of personal data and compliance with GDPR

CONSULTATION WITH DPO:
- Data Protection Officer must be consulted in the DPIA process
- DPO advice must be documented and recorded

PRIOR CONSULTATION WITH SUPERVISORY AUTHORITY (Article 36):
- Required when DPIA indicates processing results in high residual risk
- 8-week (extendable to 14 weeks) supervisory authority consultation period applies
- Supervisory authority may issue written advice or prohibit processing

Compliance Requirements:
- Complete DPIA before deploying any AI system falling in mandatory categories.
- Consult DPO in the DPIA process.
- Document DPIA findings and measures taken.
- Seek prior consultation with supervisory authority for high residual risk AI.
- Update DPIA when processing changes or new risks are identified.
- Integrate DPIA into AI system development lifecycle.
""",
        },
    ]


def _india_dpdp_regulations() -> List[dict]:
    return [
        {
            "name": "India DPDP Act – Section 4: Grounds for Processing Personal Data",
            "short_name": "DPDP Act Sec. 4",
            "jurisdiction": "IN",
            "effective_date": datetime(2023, 8, 11),
            "enforcement_date": None,  # Rules not yet notified
            "category": "Data Privacy",
            "url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
            "full_text": """India Digital Personal Data Protection Act 2023 – Section 4: Grounds for Processing Personal Data

Section 4 establishes the lawful grounds for processing personal data in India. AI systems processing personal data of Indian citizens must comply.

LAWFUL GROUNDS FOR PROCESSING:

1. CONSENT (Section 6)
   - Data Principal (individual) must give free, specific, informed, and unambiguous consent
   - Consent through a consent notice
   - Data Principal must be at least 18 years old (or guardian consent for children)
   - For AI systems: consent must cover the AI-specific processing purpose

2. LEGITIMATE USES (Section 7) – Processing without consent is permitted for:
   (a) Performance of a function or service in the interest of sovereignty or integrity of India, security of the State, friendly relations with foreign States, maintenance of public order, or prevention of any offence
   (b) Compliance with judgments, decrees, orders, or directions by courts or tribunals
   (c) Medical emergency involving a threat to life or immediate threat to health
   (d) Disaster, breakdown of public order
   (e) Employment purposes (recruitment, employment contracts, termination)
   (f) Activities by courts, tribunals, or other judicial bodies
   (g) Social welfare benefits from the State
   (h) Responding to a medical emergency

AI SYSTEM IMPLICATIONS:
- AI systems using personal data for training must have a lawful basis.
- Personal data collected for one purpose cannot be repurposed for AI training without a separate lawful basis.
- Employer AI systems (performance monitoring, hiring) may rely on employment-related legitimate uses.
- Healthcare AI must identify the appropriate ground for processing health data.

DATA FIDUCIARY OBLIGATIONS (Processing Entity):
- Only process personal data for the specified purpose disclosed to the Data Principal.
- Cannot process data beyond what is necessary for the stated purpose.
- Must implement reasonable security safeguards.

Compliance Requirements:
- Identify lawful ground for each AI system's data processing.
- Document purpose limitations for AI training data.
- Establish consent management for AI systems requiring consent.
- Map AI data flows to ensure lawful basis applies to each.
""",
        },
        {
            "name": "India DPDP Act – Sections 5 & 6: Notice and Consent",
            "short_name": "DPDP Act Sec. 5-6",
            "jurisdiction": "IN",
            "effective_date": datetime(2023, 8, 11),
            "enforcement_date": None,
            "category": "Data Privacy",
            "url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
            "full_text": """India DPDP Act – Sections 5 and 6: Notice and Consent Requirements

SECTION 5 – NOTICE:

Before collecting personal data (including for AI systems), the Data Fiduciary must provide a notice containing:
(a) The personal data and purpose for which it is sought to be processed
(b) The manner in which Data Principal may exercise their rights under the Act
(c) The manner in which complaints may be filed with the Data Protection Board

Notice requirements for AI systems:
- Must be provided before or at the time of data collection
- Must be clear and plain language (not complex legal language)
- Should explain how data will be used in automated/AI processing
- For AI training: must disclose that data may be used to train models
- Must be in English or any language specified in the Eighth Schedule of the Constitution

SECTION 6 – CONSENT:

Standards for Valid Consent:
- Free: not induced, coerced, or forced
- Specific: for a specific purpose only
- Informed: following notice under Section 5
- Unconditional: not contingent on acceptance of any terms beyond what is necessary
- Unambiguous: clear affirmative action

Consent Manager:
- Data Principals may use a consent manager (a registered entity) to give, manage, review, and withdraw consent
- The Central Government will establish a system for consent managers

Right to Withdraw Consent:
- Data Principals may withdraw consent at any time
- Withdrawal must be as easy as giving consent
- On withdrawal, Data Fiduciary must cease processing within a reasonable timeframe

AI System Specific Consent:
- Consent for AI model training must be explicitly separate from service consent
- Automated decision-making using personal data requires specific disclosure
- Children's data cannot be used for AI training without verifiable parental consent

Compliance Requirements:
- Create compliant consent notices for all AI data collection.
- Implement consent withdrawal mechanisms.
- Separate consent flows for AI training and service delivery.
- Maintain consent records and audit trails.
- Translate notices into required languages.
""",
        },
        {
            "name": "India DPDP Act – Sections 7–9: Legitimate Uses, Data Fiduciary Obligations, Children's Data",
            "short_name": "DPDP Act Sec. 7-9",
            "jurisdiction": "IN",
            "effective_date": datetime(2023, 8, 11),
            "enforcement_date": None,
            "category": "Data Privacy",
            "url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
            "full_text": """India DPDP Act – Sections 7-9: Legitimate Uses, General Obligations, and Children's Data

SECTION 7 – CERTAIN LEGITIMATE USES (Processing Without Consent):

The following are legitimate uses permitting processing without consent:
(a) State and its instrumentalities for sovereign functions, national security, public order
(b) Compliance with judicial orders and legal obligations
(c) Medical emergencies threatening life
(d) Disaster management and public emergencies
(e) Employment-related processing (recruitment, employment contracts, benefits administration, promotions, termination) – relevant for HR AI systems
(f) Disclosure to courts and tribunals
(g) Processing for social welfare programs

SECTION 8 – GENERAL OBLIGATIONS OF DATA FIDUCIARY:

1. PURPOSE LIMITATION: Use personal data only for the specified purpose.
2. DATA MINIMIZATION: Do not retain personal data longer than necessary.
3. DATA ACCURACY: Make reasonable efforts to ensure data accuracy and completeness where processing can significantly impact Data Principals.
4. SECURITY SAFEGUARDS: Implement appropriate technical and organisational security safeguards.
5. DATA BREACH NOTIFICATION: Notify Data Principals and the Data Protection Board in the event of a personal data breach in prescribed form and within prescribed timelines.
6. DATA RETENTION: Erase data when purpose is fulfilled and retention period expires.
7. ACCOUNTABILITY: Publish contact information of DPO/designated person for grievances.

Significant Data Fiduciary Requirements:
- Appointment of Data Protection Officer (Indian resident)
- Conduct Data Protection Impact Assessment (DPIA)
- Conduct data audit annually
- Additional obligations as prescribed by the Central Government

SECTION 9 – PROCESSING OF PERSONAL DATA OF CHILDREN:

Children defined as individuals under 18 years of age.

Requirements:
- Obtain verifiable consent of parent or lawful guardian before processing a child's data
- Do not process personal data of a child that is likely to cause detrimental effect on the wellbeing of the child
- Do not undertake tracking or behavioural monitoring of children
- Do not direct targeted advertising to children
- The Central Government may prescribe a higher age threshold

Implications for AI Systems:
- AI recommendation systems must not target children without parental consent
- AI emotion recognition or behavioral profiling of children is prohibited
- Age verification mechanisms are required for AI systems potentially used by children
- Parental consent management needed for educational AI platforms

Compliance Requirements:
- Implement purpose limitation for all AI data processing.
- Establish security safeguards and data breach response procedures.
- Build age verification for AI systems potentially used by minors.
- Obtain verifiable parental consent for processing children's data in AI systems.
- Notify authorities within prescribed timelines of data breaches.
""",
        },
        {
            "name": "India DPDP Act – Section 11: Right to Information About Personal Data",
            "short_name": "DPDP Act Sec. 11",
            "jurisdiction": "IN",
            "effective_date": datetime(2023, 8, 11),
            "enforcement_date": None,
            "category": "Data Privacy",
            "url": "https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf",
            "full_text": """India DPDP Act – Section 11: Rights of Data Principal (Right to Information About Personal Data)

Section 11 establishes the data subject rights relevant to AI systems in India.

RIGHT TO ACCESS INFORMATION (Section 11):

1. DATA PRINCIPAL'S RIGHT TO INFORMATION
   Data Principals are entitled to obtain from the Data Fiduciary:
   (a) A summary of personal data being processed and the processing activities
   (b) The identities of all other Data Fiduciaries and Data Processors with whom the data has been shared, along with description of data shared
   (c) Any other information related to their personal data and its processing as may be prescribed

AI System Requirements:
- Users must be able to request a summary of their data used in AI processing
- AI-driven decisions: users must be able to understand what data was used
- Sharing of data with third-party AI services must be disclosed on request

RIGHT TO CORRECTION AND ERASURE (Section 12):
- Right to correct inaccurate or misleading personal data
- Right to update incomplete personal data
- Right to erase personal data no longer necessary for the purpose for which it was processed
- Right to restriction of processing pending verification of correction/erasure request

IMPLICATIONS FOR AI SYSTEMS:
- Correction: If AI system uses incorrect data, must allow correction
- Erasure: "Right to be forgotten" requires AI systems to allow deletion of personal data
- AI models trained on individual data: erasure requests may require model updates or retraining (technical challenge)
- Must implement data lineage tracking to comply with erasure rights

RIGHT TO GRIEVANCE REDRESSAL (Section 13):
- Data Principal may register grievance with Data Fiduciary
- Data Fiduciary must resolve within timelines prescribed by the Central Government
- Data Principal can escalate to Data Protection Board if not resolved

RIGHT TO NOMINATE (Section 14):
- Data Principals may nominate another person to exercise rights on their behalf in case of death or incapacity
- Relevant for AI systems in healthcare, eldercare contexts

PENALTIES FOR NON-COMPLIANCE WITH DATA PRINCIPAL RIGHTS:
- Failure to implement security safeguards: up to ₹250 crore
- Failure to notify data breach: up to ₹200 crore
- Violation of children's data protections: up to ₹200 crore
- Failure to comply with DPB orders: up to ₹150 crore

Compliance Requirements:
- Build data access mechanisms allowing Data Principals to view their data in AI systems.
- Implement correction and erasure request workflows.
- Establish grievance redressal processes with prescribed timelines.
- Track data lineage to support erasure rights.
- Maintain records of all data principal rights requests and responses.
""",
        },
    ]


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------

def get_all_regulations() -> List[dict]:
    """Return all regulation dicts from all jurisdictions."""
    return (
        _eu_ai_act_regulations()
        + _us_regulations()
        + _gdpr_regulations()
        + _india_dpdp_regulations()
    )


def seed_regulations(db: Session) -> dict:
    """
    Populate the database with all regulation records on first run.

    Returns a summary dict with counts of inserted/skipped records.
    """
    existing_names = {r.name for r in db.query(Regulation.name).all()}
    inserted = 0
    skipped = 0

    for reg_data in get_all_regulations():
        if reg_data["name"] in existing_names:
            skipped += 1
            continue

        regulation = Regulation(
            name=reg_data["name"],
            short_name=reg_data.get("short_name"),
            jurisdiction=reg_data.get("jurisdiction"),
            effective_date=reg_data.get("effective_date"),
            enforcement_date=reg_data.get("enforcement_date"),
            full_text=reg_data.get("full_text"),
            category=reg_data.get("category"),
            url=reg_data.get("url"),
        )
        db.add(regulation)
        inserted += 1

    db.commit()
    return {
        "inserted": inserted,
        "skipped": skipped,
        "total": inserted + skipped,
    }


def is_seeded(db: Session) -> bool:
    """Check if the regulation knowledge base has been seeded."""
    count = db.query(Regulation).count()
    return count > 0
