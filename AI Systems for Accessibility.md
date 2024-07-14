## TL;DR

### Introduction to AI Systems for Accessibility

Noah and Dylan discuss AI's role in digital accessibility, focusing on human-centric, error-avoiding implementations. They recap last year's advancements, presenting new tools like AKS DevTools Pro and a Figma Plugin to assist designers with accessibility annotations.

### Current AI Systems

- **AKS DevTools Pro**: Performs guided tests to identify UI elements and markup discrepancies.
- **Figma Plugin**: Helps designers add accessibility annotations and tab indices directly.

### Advances in LLMs

Large Language Models (LLMs), such as ChatGPT, have enhanced accessibility through their ability to understand and produce human-like text, offering personalized and context-aware support.

### Human-Centric AI Approach

DK emphasizes AI systems that meet users' needs at different stages of their accessibility journey, combining LLMs with DK’s resources to create personalized and effective tools.

### New AI Tools

- **Access Advisor for DQ University**: Personalized tutor for accessibility queries.
- **DQ AI Accessibility Remediation Assistant**: Identifies and suggests fixes for accessibility issues in code based on AxCore analysis.

### Future Plans

Access Advisor and the AI Remediation Assistant are announced, with preview access available soon. These tools aim to integrate AI-driven, user-centric solutions to enhance digital accessibility practices.

# Introduction to AI Systems for Accessibility

Welcome to our talk on AI systems for accessibility. I, Noah, am thrilled to speak here for the second year about AI and machine learning in accessibility. Last year, we introduced AI systems for accessibility, and this year, we have new advanced ones to share. I've been a machine learning engineer at DK for over four years. I am joined by Dylan, an accessibility coach turned AI accessibility engineer at DK.

### Importance of Human-Centric AI in Accessibility

The speakers emphasize the significance of adopting AI in accessibility with careful consideration to avoid false positives and the potential introduction of new issues. They highlight DK's commitment to delivering AI systems that assist humans while ensuring they remain in control. This approach aims to enhance digital accessibility by using AI in a way that benefits users without compromising their autonomy or accuracy in identifying genuine accessibility issues.

### Recap of Last Year's Achievements

Last year, DK introduced state-of-the-art AI systems for accessibility, focusing primarily on proprietary computer vision algorithms and an efficient data pipeline. These innovations allow DK to identify user interface (UI) elements purely based on visual semantics, resembling how a sighted user would perceive them. The computer vision system then detects discrepancies by comparing these visual elements with the corresponding markup.

**Key Components:**

- **Proprietary Computer Vision Algorithms**
  - Identify UI elements based on visual appearance.
  - Compare visual elements with markup to detect discrepancies.

- **Applications of the System**
  - **AKS DevTools Pro**
    - *Interactive Components*: Intelligent Guided Test to identify buttons, tabs, inputs, etc.
    - *Tables*: Intelligent Guided Test to check table rows and headers for proper markup.
  - **Figma Plugin (acts for designers)**
    - Assist designers in adding accessibility annotations directly.
    - Suggest accessibility annotations for different landmark elements.
    - Provide automated tab index markers.

  By leveraging these capabilities, DK ensures accessibility from the design phase itself, addressing many issues before they even reach development. Their data show that most accessibility issues originate during the design step, making this approach highly effective.

### Current AI Systems and Their Applications

In this section, the speakers discuss the AI systems currently integrated into DK products and provide detailed examples of their applications.

#### AKS DevTools Pro
- **Intelligent Guided Tests**:
  - Uses visual semantics to identify and compare interactive and structural user interface elements based on their visual appearance.
  - **Examples**:
    - **Elements Intelligent Guided Test**: Identifies interactive components (e.g., buttons, tabs, inputs) by comparing computer vision model detections with the markup.
    - **Tables Intelligent Guided Test**: Ensures table rows and headers are marked up properly for screen reader interpretation.

#### Figma Plugin Acts for Designers
- **Integration**:
  - Allows designers to add accessibility annotations directly to their designs using the computer vision system.
  - **Features**:
    - **Suggestions for Accessibility Annotations**: Provides automated suggestions for accessibility landmarks.
    - **Automated Tab Index Markers**: Automatically generates tab index markers based on visual presentation.
  - **Purpose**: 
    - Helps prioritize accessibility from the beginning of the software lifecycle.
    - Aims to prevent accessibility issues originating in the design phase by assisting designers who may not be accessibility experts.

These examples showcase DK’s effort to leverage AI and machine learning technologies to improve digital accessibility in a user-centric manner, ensuring the developers and designers remain in control while benefiting from enhanced detection and guidance features.

### Changes in the AI Landscape Over the Past Year

The past year has seen significant developments in the AI landscape, which have expanded dramatically beyond the tech community. AI has become a central subject in various fields such as ethics and creativity, and its implications are now an everyday topic. A pivotal development has been the emergence and further advancement of large language models (LLMs).

- **Expansion Beyond Tech Community**:
  - AI is now widely discussed in ethics, creativity, and other sectors.

- **Emergence of Large Language Models**:
  - Most common example: ChatGPT.
  - Produced by various companies.
  - Their capabilities have sparked debate and excitement in different sectors.

- **Importance for Accessibility**:
  - Represents a pivotal moment for digital accessibility.
  - Potential to build person-centric technology.
  - Can offer a wealth of knowledge and adapt to individual needs.

LLMs, like ChatGPT, bring technology closer to being person-centric, capable of understanding and producing human-like text and code, which presents unprecedented opportunities for improving accessibility tools and services. However, these models also bring challenges and biases that need careful consideration to ensure they support accessibility effectively.

## Introduction to Large Language Models (LLMs)

### Overview

Noah and Dylan introduced the topic of large language models (LLMs) like ChatGPT in the context of accessibility. They emphasized that LLMs have significantly shaped the AI landscape in the past year.

### Training Data and Process

LLMs are essentially advanced text predictors. They operate on the same statistical and mathematical principles as other deep learning models but are unique due to their extensive training data and process.

- **Training Set**: LLMs are trained on a vast amount of human-written text and code, including books, academic papers, blog posts, source code, and more.
- **Corpus**: This comprehensive data set, known as the corpus, contains publicly accessible information across various styles, fields, and genres, including accessibility.

### Training Process

1. **Data Ingestion**: The model ingests a tremendous amount of data.
2. **Statistical Techniques**: Words are grouped together based on context and frequency.
3. **Graph Creation**: The model creates a large graph where points represent words, ideas, and concepts. The dimensions of the graph represent different contexts in which these points were found.
4. **Mental Model**: This process generates a mental model that encodes the meanings of words and phrases.
5. **Contextual Relationships**: Similar words and phrases are grouped together not by language or alphabetical order but by meaning. This allows for capturing depth, context, and nuance in human language.
   
### Diagram Representation

| Step              | Description                                                |
|-------------------|------------------------------------------------------------|
| Data Ingestion    | Model ingests extensive human-written text and code.       |
| Statistical Techniques | Words are grouped based on context and frequency.     |
| Graph Creation    | Large graph with points representing words, ideas, etc.    |
| Mental Model      | Encodes meanings of words and phrases in various contexts. |
| Contextual Relationships | Grouping by meaning, capturing depth and nuance.    |

By processing this way, LLMs demonstrate a high level of understanding of language, surpassing previous natural language processing systems.

### Capabilities and Applications of LLMs in Accessibility

#### Examples Demonstrating Contextual Understanding
Dylan showcases the contextual understanding capabilities of ChatGPT using two examples. The first example is a personal story about a dog named Basil eating banana muffins. In this context, ChatGPT defines "bad girl" as expressing affectionate disapproval. The second example involves analyzing Charli XCX song lyrics, where "bad girl" means someone who is self-confident and captivating. These examples illustrate the model's ability to interpret contextual meaning accurately.

#### Role Adaptation and Audience Targeting
Dylan further demonstrates how LLMs can adapt their responses based on the role they are asked to play and the audience they are targeting. For instance, when asked to explain the term "perceivable" in the context of the Web Content Accessibility Guidelines (WCAG):

1. **Control Output:** General explanation without specific audience targeting.
2. **Role Adaptation:** Acting as an accessibility expert, providing a more detailed and technical response.
3. **Audience Targeting:** Tailoring the answer for a beginner, using simple language and analogies.

These capabilities allow LLMs to provide more relevant and customized responses depending on the user's level of expertise and context, enhancing their utility in accessibility applications.

### Challenges and Pitfalls of LLMs in Accessibility

The document discusses the potential and pitfalls of Large Language Models (LLMs) like ChatGPT in the field of accessibility. Despite their advanced capabilities, LLMs inherit biases and errors from their training data, which is sourced from the internet. This result in the models potentially outputting the same accessibility mistakes found in the data they were trained on.

#### Key Points:
- **Inherited Biases and Errors**:
    - Base models like ChatGPT are trained on internet data, which includes biased and incorrect information.
    - These models may produce accessibility errors similar to those prevalent in the training data.

- **Importance of Human Oversight**:
    - Careful prompting and the use of additional information can help mitigate these biases.
    - Example prompts like “act as a digital accessibility professional with a focus on WCAG performance” can guide the model to output more reliable information.

- **Customization and Adaptability**:
    - Models can be customized with specific commands and additional training to improve their output reliability.
    - Human oversight is crucial for verifying and correcting the model’s output to ensure that it provides accurate and accessible results.

In conclusion, while LLMs offer significant potential for improving accessibility tools and services, their use must be carefully managed to avoid propagating biases and errors. This underscores the importance of maintaining human control in the deployment of these systems.

### Human-Centric Approach in AI Systems

The document emphasizes the importance of a human-centric approach in AI systems, particularly in the context of digital accessibility. The key points covered include:

- **Meeting Users Where They Are**: It's crucial for AI systems to meet developers, designers, and product owners at their specific point in their accessibility journey. This approach contrasts with the current system, where individuals must read through extensive documentation and courses, often without knowing what specific information they need.

- **Combining Capabilities of LLMs with DK’s Resources**: The flexibility and understanding of natural human input by large language models (LLMs) are combined with DK’s world-class accessibility resources, tooling, and analytics. This creates tailored experiences based on the user's level of expertise and contextual needs.

- **Current System’s Shortcomings**: Most beginners start their accessibility journey under stressful and complicated conditions, such as tight deadlines due to lawsuits. This situation can lead to a frustrating experience, preventing real change and making it challenging to understand the nuanced and complex world of digital accessibility.

- **Potential of AI Systems for Accessibility**: The combined abilities of LLMs and DK’s resources can create personalized accessibility tutors and remediation tools. These tools can integrate seamlessly, providing immediate actionable steps and learning aids that are contextually relevant and tailored to the user's needs.

- **Preventing Frustration and Improving Accessibility**: Tailored systems can demystify accessibility concepts, reduce the barriers of entry for beginners, and help them avoid becoming frustrated. This approach is seen as beneficial for promoting inclusive practices within organizations.

The overall aim is to create systems that do not solely depend on individual efforts to seek out information but rather bring tailored, role-specific, and contextually appropriate support to ensure accessibility compliance and understanding.

### Announcing New AI Accessibility Tools

#### Introduction to New Tools
Noah and Dylan announced two new human-centric AI applications aimed at enhancing accessibility. These tools are:

1. **Access Advisor for DQ University** 
2. **DQ AI Accessibility Remediation Assistant for Dev Tools**

#### Overview of Access Advisor
Noah described Access Advisor as a personalized accessibility tutor that adapts to the user's level and specific situations. Integrated directly into DQ University, it provides a judgment-free zone for users to ask questions, ranging from basic to complex. It's especially useful for users who might feel embarrassed about their questions.

##### Example Interaction with Access Advisor
In the example provided:
- The user asked, "So this may seem like a stupid question, but how can people use a website if they can't see them or use a mouse to get around?"
- Access Advisor responded reassuringly and broke down the question into multiple parts, addressing how blind users use screen readers and how people who can't use a mouse may use voice recognition software.
- The response included links to DQ University courses for further in-depth reading.

All answers are rooted in course content from DQ University, ensuring reliable and trustworthy information.

#### Overview of DQ AI Accessibility Remediation Assistant
Dylan introduced this tool as the most ambitious AI system yet. This tool guides AI models through uncovering the root cause of an accessibility issue using a combination of AxCore issues and contextual code analysis.

##### Detailed Process of the Remediation Tool
The tool:
1. Analyzes the HTML code and identifies issues based on AxCore.
2. Determines the developer’s intention behind the code.
3. Attempts to address the issue while preserving the coding style.
4. Provides actionable tips and feedback to help developers avoid these issues in the future.

##### Example Remediation Scenarios
Two examples were provided:
- **Input Element Without a Label:**
  - The AI analyzed a promo code input without a label, identified the issue, and provided two recommendations: one using a native label element and another suggesting ARIA-label.
- **Invalid Custom Heading:**
  - The AI identified a paragraph tag styled as a heading and provided fixes including using an H1 tag or adding a role attribute set to "heading".

The system validates its recommendations through multiple checks before presenting them to the user.

#### Availability and Future Access
Noah and Dylan stated that pricing information for Access Advisor would be announced soon, and users can sign up for preview access via a QR code. The availability for the AI accessibility remediation integration is still to be announced. They encouraged users to stay updated through DQ’s News and Resources page.

This new suite of tools represents a significant step forward in making digital accessibility more approachable and effective, leveraging AI to provide nuanced, context-aware assistance to users at various stages of their accessibility journey.

### Demo of Access Advisor for DQ University

#### Overview of Access Advisor
Access Advisor is a personalized accessibility tutor integrated directly into DQ University. It adapts DQ’s body of knowledge about accessibility to the user's individual level and particular learning context.

#### Example Interaction
- The user initiates a conversation by asking a question that might seem embarrassing or basic to them.
- Access Advisor responds with a friendly and reassuring tone, breaking down the question into multiple parts:

  1. **For Blind Users**:
     - Describes how blind users use screen readers to navigate websites.
     - Provides a link to the DQ University course: ["Design Considerations for Blindness"](I Don't Know).

  2. **For Users Who Can't Use a Mouse**:
     - Explains how users with dexterity or motor disabilities might use voice recognition software.
     - Provides a link to the DQ University course: ["Design Considerations for Dexterity and Motor Disabilities"](I Don't Know).

- The response ensures a beginner-level understanding and offers citations to trusted resources for further learning. 

#### Features and Benefits
- **Friendly and Reassuring Tone**: Addresses user queries in a non-judgmental manner.
- **Context-Specific Answers**: Provides detailed explanations based on the provided context.
- **Trusted Citations**: Links responses to DQ University courses for reliable information.
- **User-Friendly Interface**: Allows users to interact and learn without fear of asking "stupid" questions.

#### Impact
This tool aims to foster a comfortable and supportive learning environment for all users, ensuring that learners can ask any questions and receive detailed, trustworthy responses. This approach helps in demystifying complex accessibility topics and allows users to enhance their understanding at their own pace.

```markdown
| Feature              | Description                                                                           |
|----------------------|---------------------------------------------------------------------------------------|
| Friendly Tone        | Provides a supportive and non-judgmental interaction.                                  |
| Context-Specific     | Delivers tailored information based on user queries.                                   |
| Trusted Citations    | Includes links to DQ University courses for further, in-depth learning.                |
| User-Friendly        | Encourages questions without fear of embarrassment, catering to all learning levels.   |
```

#### Availability
Access Advisor will soon be available for preview access. Interested users can enroll via a QR code or link provided in the presentation.

I hope this detailed breakdown of the demo for Access Advisor illustrates its potential impact on learning digital accessibility skills.

## Demo of AI Accessibility Remediation Tool

### Overview of the Remediation Process
The AI Accessibility Remediation tool represents a significant advancement in accessibility technology. The tool analyzes code for accessibility issues, determines developer intentions, and provides actionable remediation recommendations while preserving the coding style. Here’s an example-driven walkthrough to illustrate its functionality.

### Process Steps
1. **Issue Detection**: Uses Ax core to flag an issue within the code.
2. **Context Extraction**: Selects surrounding HTML context for the flagged issue.
3. **Intent Analysis**: Determines the likely intention of the developer from the context clues.
4. **Issue Analysis**: Identifies the specific cause of the accessibility issue.
5. **Disability Considerations**: Lists the types of disabilities affected by the issue.
6. **Remediation Tips**: Provides actionable tips to resolve the issue.

### Example 1: Missing Input Label
- **Input HTML**:
    ```html
    <input class="promo-code-input">
    ```
- **Detected Issue**: The input element lacks an associated label.
- **Developer Intent**: Determines the input is for promo codes.
- **Disability Concerns**: Highlights issues for screen reader and voice recognition software users.

### Analysis and Recommendations
- **Semantic Recommendation**:
    ```html
    <label for="promo-input">Promo Code</label>
    <input id="promo-input" class="promo-code-input">
    ```
- **Minimal Changes Recommendation**:
    ```html
    <input aria-label="Promo Code" class="promo-code-input">
    ```

### Example 2: Invalid Custom Heading
- **Input HTML**:
    ```html
    <p aria-level="1"><span style="font-size: 2em;"><strong>Important Heading</strong></span></p>
    ```
- **Detected Issue**: The paragraph tag is styled to look like a heading but does not support `aria-level`.
- **Developer Intent**: Intended to represent a heading.
- **Disability Concerns**: Issues for users relying on assistive technologies for heading navigation.

### Analysis and Recommendations
- **Semantic Recommendation**:
    ```html
    <h1>Important Heading</h1>
    ```
- **Minimal Changes Recommendation**:
    ```html
    <p role="heading" aria-level="1"><span style="font-size: 2em;"><strong>Important Heading</strong></span></p>
    ```

### Validation Process
Before presenting recommendations to users, solutions are validated through:
- **Acts Core API Check**: Ensuring no additional issues are introduced.
- **Sanity Check by Another AI Model**: Verifying the solution maintains the developer's intent.

### Summary
The AI Accessibility Remediation tool not only provides tailored, actionable steps to resolve issues but also educates developers on best practices, emphasizing flexibility and the application of accessible code without disrupting existing coding styles. This dual approach ensures accessibility improvements are practical and integrated seamlessly into current workflows.

### Future Availability and Announcement

The future availability and announcement section highlights key details about the new AI accessibility tools introduced by DK:

#### Access Advisor for DQ University

- **Pricing Information**:
  - Pricing details for Access Advisor will be announced soon.

- **Availability**:
  - Access Advisor will be open for preview access shortly.
  - Individuals looking to try Access Advisor as soon as possible can enroll for early access using the provided QR code or link.

> Here's a summary of the steps to stay updated and enroll for early access:
> 
> | Step | Action |
> |------|--------|
> | 1    | Monitor announcements for pricing information. |
> | 2    | Scan the QR code or use the provided link to enroll for early access. |
> | 3    | Provide feedback once you have access to further improve the tool. |

#### AI Accessibility Remediation Integration

- **Current Status**:
  - The AI Accessibility Remediation tool integration within Ax DevTools Pro is still in development.
  - The release date for this integration has yet to be announced.

- **Stay Updated**:
  - Users can stay informed about updates and news related to DK’s accessibility tools by visiting the News and Resources page or following updates shared by chat moderators.

The DK team emphasizes its commitment to ensuring these integrations meet their high standards and deliver a smooth user experience with minimal issues.

### Q&A Session

During the Q&A session, several key questions were answered regarding the AI accessibility tools presented:

- **Data Capture by AI Accessibility Remediation Tool**: The tool captures a selector of the code causing the issue and the related Ax Core issue. It selects necessary semantic HTML for context and analyzes the developer's intention based on context clues within the code.

- **Signaling Tone for Ax Advisor**: Ax Advisor adapts its responses based on the user's familiarity with accessibility, which can be determined by their progress through DQ University’s curriculum or possibly through user settings indicating their experience level.

- **Tool Deployment**: Currently, the primary application of the AI accessibility remediation tool is within Ax Dev Tools Pro, but it could potentially be adapted for other contexts such as DQ University. The availability and further integration details are still under development.

- **Handling Incorrect Developer Intent**: If the AI misinterprets the developer’s intent, a human-in-the-loop approach allows the user to provide feedback and correct the model. This ensures the final solution aligns with the developer's true intention.

- **Feedback on Ax Advisor**: Developers can incorporate company standards or specifics into Ax Advisor's recommendations. The system will consider these factors when formulating responses. Users will also have the option to provide feedback to refine and improve the recommendations continuously.

#### Example of Data Handling
| Question                                 | Answer                                                                                                 |
|------------------------------------------|--------------------------------------------------------------------------------------------------------|
| What kind of data does the remediation tool capture from a user? | The tool captures selector of the code causing the issue and the related Ax Core issue. It also selects necessary semantic HTML for context. |

#### Example of Tone Signaling
Ax Advisor can automatically adjust its response based on the user’s experience level, either inferred or explicitly set by the user. 

### Key Points
- **Human-Centric Design**: Ensuring the human remains in control is critical, particularly for correcting potential misinterpretations by AI models.
- **Context and Nuance**: Accurate and context-aware responses are needed to handle the complexities of accessibility.

This session emphasized the importance of adaptability, customization, and user feedback in enhancing the AI tools for accessibility presented by Noah and Dylan.