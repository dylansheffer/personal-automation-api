# ZERO Cost AI Agents: Are ELMs ready for your prompts? (Llama3, Ollama, Promptfoo, BUN)

## TL;DR

Emerging Efficient Language Models (Elms) like Llama 3 and Gemma 53 are revolutionizing on-device AI by cutting costs and boosting innovation. The ITV Benchmark evaluates these models on accuracy, speed, memory, and context handling. Models like Llama 3 are nearing readiness, with significant advancements expected by 2024.

## Detailed Summary

### Introduction

---

#### Overview of Elm and Llama 3

Gemma 53 and Llama 3 are open-source language models gaining viability with each release. Apple's new open Elm model is also mentioned, highlighting the growing importance of Efficient Language Models (Elms) in the LLM ecosystem.

#### Importance of Elms

Elms are crucial as they revolutionize the business model of agentic tools and products. Running prompts directly on a device can reduce building costs to zero, enhancing innovation speed.

#### Cost Savings and Innovation with On-Device Elms

Running Elms on-device significantly reduces costs, fostering rapid innovation. The introduction of models like Llama 3 exemplifies this trend.

#### Core Question: Are Efficient Language Models Ready for On-Device Use?

The core question addressed in the video is whether efficient language models are ready for on-device use and how one can determine if an Elm meets their standards. The video aims to explore:

- Necessary standards for Elms, including RAM consumption, tokens per second, and accuracy.
- Attributes needed for Elms to function effectively on-device.
- The ITV Benchmark as a tool to assess if a model meets specific use cases.
- Practical examples of running benchmarks on devices like the M2 MacBook Pro with 64 GB of RAM.

#### Key Questions and Standards

- Set standards for what Elm attributes are important (e.g., RAM consumption, tokens per second, accuracy).
- Detailed analysis of where Elms need to be to function on-device.
- Introduction and breakdown of the ITV Benchmark to evaluate if a model is suitable for specific use cases with practical examples.

#### Personal Approach to Building Agentic Tools and Products

The discussion includes personal standards for determining if an Elm is ready for on-device use:

1. **Accuracy and Speed**
   - Accuracy: It is crucial, with a pass rate requirement discussed.
   - Speed: Measured in tokens per second; speed is essential for usability.

2. **Memory and Context Window**
   - Memory: Evaluations on RAM consumption and GPU/CPU usage.
   - Context Window: Evaluating the context window's size and its impact.

3. **JSON Response and Vision Support** 
   - Overview of the necessity of JSON response and vision capabilities.

4. **Setting Personal Standards**
   - Importance of defining personal benchmarks for accuracy, speed, memory consumption, and context windows to ensure Elms meet specific use cases.

#### Conclusion

The video aims to answer if Elms are ready for on-device use and outlines steps to determine the readiness of language models for personal or professional usage through benchmarks and example setups. 

---

The subsequent sections will further delve into specific metrics, standards, and practical examples to substantiate the claims and evaluations outlined in this introduction.

## Key Metrics and Standards for Elms

---

### Accuracy and Speed

**Accuracy** and **Speed** are pivotal metrics for evaluating Elms:

- **Accuracy Assessment**
  - Determines if the model performs well for specific use cases.
  - Consider establishing a pass rate, such as 80% or higher, for a model to be deemed acceptable.
  - Critical benchmark as accuracy can be a dealbreaker if it does not meet the required standard for the intended use.

- **Speed Measurement**
  - Measured in tokens per second (TPS).
  - Range from 1 TPS up to high-performance models achieving over 1,000 TPS.
  - Speed is crucial as it directly impacts the usability and efficiency of the model. If the speed is too low, it becomes a complete blocker for implementation.

### Memory Consumption

**Memory Consumption** is a major constraint for Elms, affecting their feasibility for on-device use:

- Elms can consume anywhere from 4 GB of RAM to more than 128 GB.
- Running large models like Llama 3 with 70 billion parameters can significantly tax available RAM, sometimes using up to half of a high-end device's memory.
- Efficient memory usage is necessary to ensure Elms can run without overwhelming the device, thus balancing performance and resource utilization.

### Context Window

**Context Window** defines how much text the model can handle at once:

- Targets a minimum of 32k tokens for effective use.
- Llama 3's 8K context window, although decent, may be too small for larger prompts and more extensive prompt chains.
- An adequate context window length is crucial for handling complex tasks and chaining multiple prompts.

### JSON Response and Vision Support

These are additional features that support broader use cases:

- **JSON Response**: Essential for structured data outputs and integrations with other systems.
- **Vision Support**: While not a priority for all use cases, it is a valuable addition for multimodal interactions.
- Focus remains on basic "yes/no" capabilities, determining if a model has these features rather than their depth or complexity.

### Personal Standards and Benchmarks

When setting personal standards for Elms, consider the following key metrics:

- **Accuracy**: Must hit a benchmark, for example, 80% pass rate.
- **Speed**: Looking for a minimum of 20 TPS to be viable for production use.
- **Memory Consumption**: Preferably under 32 GB to fit within typical device constraints.
- **Context Window**: Aiming for at least 32k to accommodate larger and more complex use cases.
- **JSON Response and Vision Support**: Depend on the specific application needs but are generally useful additions.

By focusing on these metrics, users can better evaluate and prepare to implement Elms in their device-specific use cases, ensuring cost efficiency and enhanced innovation.

--- 

These metrics and standards form the foundation for evaluating the readiness and effectiveness of Elms in various on-device applications, ensuring they meet the specific requirements and constraints of each user's environment.

## Detailed Summary

### Detailed Breakdown of Standards

---

#### Accuracy

Accuracy is paramount when evaluating Efficient Language Models (Elms). The main points discussed include:

- **Thresholds**: Defining acceptable accuracy thresholds, such as 80% in the specific context of the ITV Benchmark.
- **Validation**: Ensuring that the model consistently meets or exceeds this threshold across various test sets.

A quote from the transcription highlights the importance:
> "The accuracy for the ITV Benchmark... must hit 80%. So if a model is not passing about 80% here, I automatically disqualify it."

#### Speed

Speed is another critical metric, discussed in terms of Tokens Per Second (TPS):

- **Minimum Speed**: Setting a minimum acceptable speed, for example, 20 tokens per second for production environments.
- **Range**: Evaluating a range from one token per second up to higher speeds like 500+ tokens per second, aiming for optimal performance without compromising on other aspects.

The transcription emphasizes:
> "Tokens per second: I require at least 20 tokens per second minimum... If it’s below this, it's honestly just not worth it."

#### Memory

Memory consumption of Elms is a vital constraint:

- **Limitations**: Describing acceptable memory usage; for instance, a maximum of 32 GB of RAM on a 64 GB device, to allow for concurrent applications like Docker instances.
- **Efficiency**: Ensuring the model operates within these memory limits without excessively consuming resources.

A mention from the video:
> "For me, I am only willing to consume up to about 32 GB of RAM."

#### Context Window

The size of the context window is essential for handling larger prompts and workflows:

- **Minimum Requirement**: Setting the minimum requirement, such as 32K context window, to ensure it can handle complex and extended sequences efficiently.
- **Comparison**: Benchmarking models like Llama 3, which may initially offer an 8K context window, against the desired standard.

A relevant section:
> "Context window for me, The Sweet Spot is 32k and above... Llama 3 released with 8K... benchmarks look great, but it's a little too small for some of the larger prompts..."

#### Practical Setup and Execution

Executing benchmarks and evaluating practical setups involve several steps:

- **Testcases**: Defining various test categories and ensuring the Elm meets predefined benchmarks.
- **Execution**: Running the ITV Benchmark on local devices, such as an M2 MacBook Pro, to evaluate real-time performance.

An illustrative quote:
> "We’re going to actually run the ITV Benchmark on Gemma 53 and Llama 3 for real on-device use."

#### JSON Response and Vision Support

While JSON response and vision support are not the primary focus, their presence or absence is noted as a qualitative attribute:

- **Necessity**: Determining the essential need for JSON response and whether vision support is a priority.
- **Current State**: Understanding that these are often built into models but may not be critical for immediate implementation.

A brief mention:
> "We’re not going to focus on these too much... more yes or no... do they have it or do they not?"

---

This detailed breakdown ensures a comprehensive understanding of the critical standards and metrics used to evaluate the readiness and efficiency of language models for on-device use.

## Introducing the ITV Benchmark

---

### Definition of the ITV Benchmark

The ITV Benchmark is a personalized, use case-specific benchmark designed to quickly swap in and out Efficient Language Models (Elms) to determine their viability for specific tools and applications. The core objective of this benchmark is to answer the question, "Is this Elm viable?" by evaluating if on-device language models are sufficiently performant for practical use cases.

### Overview of the Benchmark Process

The ITV Benchmark process is straightforward and involves setting up the benchmark environment, running the models, and analyzing their performance. Here’s a high-level breakdown:

1. **Setup:**
   - Clone the code repository provided in the video (link will be in the description).
   - Follow the readme for setting up the environment in less than a minute.

2. **Running the Test:**
   - Use simple commands to kick off testing. For example, running the command `bun run elm` initializes the test.
   - The benchmark runs multiple models, including a control model (e.g., GPT-3.5) and experimental local Elms (e.g., Llama 3, Gemma 53).

3. **Analyzing Results:**
   - Results show the pass/fail rate for each test case.
   - It provides a comparative analysis of local versus cloud-based models.
   
### Required Tools: Bun, Ollama, Promptfoo

The ITV Benchmark leverages several tools to create a seamless benchmarking experience:

1. **Bun:**
   - An all-in-one JavaScript runtime used for initializing and running the benchmark.
   - Bun has matured significantly, now supporting Windows, Mac, and Linux, making the codebase cross-platform.

2. **Ollama:**
   - Serves the local language models.
   - Ensures that the models are tested in a controlled, local environment.

3. **Promptfoo:**
   - A crucial tool for testing individual prompts against predefined expectations.
   - Facilitates detailed assertions on the output of language models, such as checking if specific strings are included or if responses meet latency and cost criteria.

   ```bash
   bun run elm
   # Initiates the test
   bun view
   # Opens a local server to visualize test results
   ```

### Practical Example: ITV Benchmark on an M2 MacBook Pro

The presenter demonstrates the ITV Benchmark on an M2 MacBook Pro with 64 GB of RAM:

1. **Initialization:**
   - The benchmark initializes models like GPT-3.5, Llama 3, and Gemma 53.
   
2. **Run and Analysis:**
   - The command `bun run elm` kicks off the test suite.
   - Results include success and failure rates across various test cases such as string manipulation, command generation, code explanation, and text classification.
   
3. **Control and Experimental Groups:**
   - Comparison is made between the control (ex: GPT-3.5) and experimental local models.
   - Provides a clear indication of how close the local models are to meeting set standards.

4. **Output Visualization:**
   - Uses `bun view` to display results on a local server.
   - Summary of the results shows the accuracy rates, comparing control to experimental groups.
   
   ```plaintext
   Control Group: GPT-3.5 - 91% accuracy
   Experimental Group: Llama 3, Gemma 53 - varied success rates
   ```

### Summary of Findings

- **Accuracy:** The benchmark helps identify if Elms meet the required accuracy, here defined as 80%.
- **Tokens per Second (TPS):** Measures the speed of prompt processing, aiming for at least 20 TPS.
- **Memory Consumption:** Ensures models use a manageable amount of RAM (e.g., less than 32 GB).
- **Context Window:** Evaluates if the context window size meets the needs for larger prompts and workflows.

### Conclusion

The ITV Benchmark provides a robust framework for evaluating the readiness of Elms for on-device use. By setting up and running this benchmark, users can ascertain if the language models they are interested in can meet their specific application requirements, thereby facilitating informed decision-making in incorporating these models into their tools and products.

## Step-by-Step Guide to Running the ITV Benchmark

---

### Setup Instructions

1. **Codebase Access and Initial Setup**
   - The codebase for the ITV Benchmark is designed to be user-friendly and adaptable.  
   - Instructions to access and set up the code will be available in the readme file of the repository.
   - Steps include basic setup like cloning the repository, installing dependencies using Bun, and opening the code in VS Code.

2. **Bun Configuration**
   - Bun is used as the all-in-one JavaScript runtime. Ensure you have Bun installed.
   - Run `bun setup` to configure the environment.

3. **Elm Configuration**
   - Configure local language models such as Llama 3, Gemma 53, etc.  
   - Update any model-specific configuration files, like defining the Llama 3 8 billion parameter model with 4-bit quantization.

### Running the Models

1. **Command Execution**
   - Open terminal and run `bun run elm` to initiate the benchmark.
   - The system will start with a defined set of models, often including GPT-3.5 as a control model, followed by Llama 3, Gemma, and other chosen Elms.

2. **Test Cases and Execution**
   - The benchmark runs through 12 predefined test cases which include string manipulation, command generation, code explanation, text classification, and more.
   - Example prompt and expected outputs are described in test files, ensuring easy customization according to specific needs. 

3. **Live Monitoring**
   - During execution, live metrics on token generation speed and accuracy are displayed. 
   - Use `bun view` to spin up a local server for detailed test results.

### Analysis of Results

1. **Result Interpretation**
   - Evaluate the percentage of tests passed per model. A personal standard mentioned is 80% accuracy rate.
   - Speed is measured in tokens per second, with 20 tokens per second as the minimum standard.

2. **Comparative Analysis**
   - Compare local Elms against a control model like GPT-3.5 to gauge performance differences.
   - Analyze test case-specific performance to determine strengths and weaknesses.

3. **Assertion Types**
   - Test cases incorporate different assertion types like equality checks for exact responses and containment checks for flexible outputs.
   - Focus on key metrics: accuracy of responses, cost efficiency, and execution latency.

### Detailed Example of a Benchmark Run

1. **Test Execution Example**
   - A practical run with models like Llama 3 will be shown with output results.
   - Reported metrics include each test case's pass/fail status, displaying comprehensive analysis through the `bun view` interface.

2. **Sample Test Cases**
   - Example of a text classification test: Prompting "Is the following block of text a SQL natural language query? Respond with yes or no."
   - Validate outcomes and responses, ensuring models meet the personal benchmark criteria set.

3. **Output Visualization**
   - The benchmarking tool provides summary results and detailed breakdowns for easy comprehension.
   - Comparison graphs and tables help in visual analysis of each model's performance across different test cases.

This comprehensive guide underscores the need for precise benchmarks to evaluate if efficient language models are ready for on-device use. It also emphasizes the importance of running tailored, practical tests to ensure alignment with personal or professional requirements. 

--- 

The detailed steps ensure that users can effectively implement and evaluate the ITV Benchmark for their specific use cases, providing a real-world example to illustrate the process and result analysis.

## Review of Test Cases and Prompts

---

### Breakdown of Test Categories

The video highlights the importance of categorizing test cases to evaluate the performance of Elms systematically. The test cases are segmented based on the following categories:

1. **String Manipulation**
   - Tasks involving string operations and transformations.

2. **Command Generation**
   - Generating executable commands or instructions.

3. **Code Explanation**
   - Explaining code snippets or programming concepts.

4. **Text Classification**
   - Classifying or categorizing pieces of text based on given criteria.

5. **Other Customized Tests**
   - Additional tests specific to individual needs or use cases.

### Example Test: Text Classification

An example of a text classification test is detailed, showcasing the methodology:

- **Prompt:**
  Provides a block of text, asking if it represents a SQL Natural Language Query (NLQ) with a simple "yes" or "no" response.
  
- **Task:**
  The prompt tests the model's ability to determine if the text is indeed a SQL NLQ and respond precisely and accurately.

- **Response Validation:**
  Uses an assertion to ensure the response is exactly "yes".

Here's a breakdown of the particular test discussed:
```markdown
Prompt: "Is the following block of text a SQL natural language query (NLQ)? Respond exclusively with yes or no."
Block of Text: "Select 10 users over the age of 21 with a Gmail address."

Expected Result: "yes"
```
The test checks both the correctness (understanding the task) and precision (providing an exact "yes" response).

### Analysis of Pass/Fail Cases

The video explores the results of running these test cases on various models, including Llama 3, Gemma 53, and others:

- **Results:**
  - **Llama 3:** Achieved nearly 80% accuracy, performing closely to the established standards.
  - **Gemma 53:** Struggled with some tests, showing about 50% success.
  - **Other Models:** Had varying levels of success, highlighting the need for continuous testing and refinement.

- **Failure Analysis:**
  Detailed examination of why specific test cases failed, including incorrect responses, partial responses, or unexpected behavior from the models.

- **Improving Test Suites:**
  The video stresses the importance of refining and expanding test cases to cover more scenarios and use cases.
  
- **Validation Efforts:**
  Special emphasis on having a control group (like GPT-3.5 Turbo) to compare against local models, providing a benchmark for ensuring competitive performance.

### Conclusion

The review of test cases and prompts illustrates the process of robustly evaluating Elms through a comprehensive suite of tests. This approach ensures that models are ready for specific use cases, helping users achieve higher confidence and utilization efficiency.

By setting rigorous standards and continuously refining the test cases, the video directs how to systematically assess and improve the performance of efficient language models, ensuring they meet the necessary criteria for on-device deployment.

## Insights from the ITV Benchmark Results

---

### Summary of Findings

The results of the ITV Benchmark, which is designed to evaluate the viability of Efficient Language Models (Elms) for on-device use, show a nuanced landscape of performance across different models. The key highlights include:

- **Accuracy and Speed**: 
  - Llama 3 achieved nearly 80% accuracy, which is close to the desired benchmark.
  - The speed measured in tokens per second (TPS) generally met the minimum standards, with some models performing better than others.

### Comparison Between Models

Various models were benchmarked, including Llama 3, Gemma 53, and others. The comparison focused on several aspects:

- **Performance Metrics**:
  - **Llama 3**: Performed well, narrowly missing the 80% accuracy mark with a score close to it.
  - **Gemma 53**: Achieved a performance where it passed 7 out of 12 test cases.
  - **GPT-3.5**: Used as a control model, it achieved a 91% pass rate, providing a high-performing benchmark.
  
- **Specific Test Results**: Each model was run through the same suite of tests designed to stress various capabilities, from text classification to command generation.

### Performance Evaluation of Llama 3, Gemma 53, and Others

- **Llama 3**:
  - Narrowly missed the 80% accuracy threshold.
  - Achieved TPS in acceptable ranges, typically around 12 TPS.
  
- **Gemma 53**:
  - Passed 7 out of 12 test cases, indicating room for improvement.
  - Similar TPS to Llama 3 but slightly lower accuracy.

- **Other Models**: Additional models showed varying degrees of performance, affirming the critical differences in capabilities depending on the specific use case and test configuration.

### Detailed Analysis

- **Accuracy**: Both Llama 3 and Gemma 53 showed promising accuracy levels, but there is still a gap to close before they can universally meet most demanding benchmarks.
- **Speed**: The TPS for most models was around 12, which is sufficient for many use cases but could be improved for more demanding applications.
- **Memory Usage**: Detailed memory consumption figures were evaluated, critical for determining the feasibility of running these models on personal devices.
- **Context Window**: Evaluated with a focus on the 32K context window as the desired minimum for complex prompts and chains.

### Conclusion

The ITV Benchmark results suggest that while models like Llama 3 and Gemma 53 are approaching the required standards for accuracy, speed, and memory usage to be viable for on-device use, there is still progress to be made. By refining these models and running them through comprehensive benchmarks, users can better understand and prepare for their deployment in real-world applications.

## Future Outlook for Efficient Language Models

---

### Predictions for 2024

#### Advancements in Local Model Capabilities

- It is anticipated that by 2024, efficient language models (Elms) will have significantly improved.
- The trend indicates the possibility of running high-performing models like a high-performance version of GPT-4 on local devices with less than 8 GB of RAM.

### Expected Improvements with Future Releases

#### Reduction in Resource Requirements

- Future releases of Elms are expected to consume fewer resources, making them more viable for on-device use.

1. **Memory Consumption**
   - Memory requirements for running large models locally are projected to decrease.
2. **Speed and Accuracy Enhancements**
   - Models are likely to become faster and more accurate.

#### Increased Usability

- Optimizations in Elms will enhance the usability of local models for complex tasks, making them suitable for a broader range of applications.
- Innovations in frameworks and tooling will simplify the deployment and testing of these models on personal devices.

### Scaling and Adapting Efficient Language Models

#### Expansion of Use Cases

- With improved efficiency, Elms can be scaled to support more extensive and varied use cases, from simple automation tasks to complex decision-making processes.
- On-device models will become more adaptable to individual user needs and specific prompt chains.

#### Evolution of Tools and Infrastructure

- Tools like Bun, Ollama, and Promptfoo will continue to evolve, offering better support and more features tailored for efficient deployment and benchmarking of Elms.
- Cross-platform support and integration improvements will facilitate seamless model testing and deployment across different operating systems.

### Concluding Thoughts

The video emphasizes that as Elms continue to evolve, they will increasingly meet the demands of on-device use. The community's collaborative efforts in improving models and supporting tools provide optimism for the near future, where Elms could reach the capabilities of current cloud-based models but with the significant advantage of lower costs and enhanced innovation potential.

---

The focus on consistent improvements and community-driven innovation underscores the promising outlook for efficient language models in the coming year and beyond.

## Conclusion

---

### Addressing the Core Question

The video ultimately tackles the question: "Are efficient language models ready for on-device use?" By leveraging tools like the ITV Benchmark and using frameworks such as Promptfoo, the video demonstrates how to determine if an Elm meets personal or professional standards. Through comprehensive testing and benchmarking, the video suggests that, for specific use cases, efficient language models are on the cusp of being ready for prime time.

---

### Closing Thoughts and Encouragement

The closing thoughts emphasize the rapid advancements in the field of efficient language models. The video encourages viewers to stay engaged with the community and to keep experimenting with and testing new models. The emphasis is on being proactive and setting personal benchmarks to ensure readiness for on-device use, saving time and money in the process.

---

### Call to Action: Engaging with the Community

- **Test and Benchmark**: Users are encouraged to use the provided codebase and benchmarks to test local models.
- **Customization**: There’s a call to customize benchmarks to fit individual use cases.
- **Stay Updated**: Viewers are asked to keep up with the community and advancements in Elms to be early adopters.
- **Participate in Discussions**: Engaging with the community through discussions and sharing insights will help in the collective advancement of efficient language models.

The conclusion underscores the importance of community collaboration and continuous experimentation, aiming for the collective goal of achieving functional and efficient on-device language models.