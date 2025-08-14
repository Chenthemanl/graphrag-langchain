"""
Academic Literature Review Prompt Templates
Based on rigorous academic methodology and the 5 C's framework
"""

from typing import List

class AcademicPromptTemplates:
    """
    Comprehensive prompt templates for literature review generation
    """
    
    @staticmethod
    def get_scoping_prompt(topic: str) -> str:
        return f"""
        You are an expert academic researcher conducting a literature review on "{topic}".
        
        TASK: Develop a comprehensive research scope and question framework.
        
        Based on the available knowledge base, perform the following analysis:
        
        1. RESEARCH QUESTIONS DEVELOPMENT:
           - Formulate 3-5 specific, answerable research questions
           - Ensure questions are focused yet comprehensive
           - Questions should follow the format: "What does the literature reveal about..."
           - Include both descriptive and analytical questions
           - Prioritize questions by importance and feasibility
        
        2. CONCEPTUAL SCOPE DEFINITION:
           - Define key terms and concepts
           - Identify the theoretical boundaries
           - Specify what is included/excluded
           - Determine the appropriate level of analysis
        
        3. METHODOLOGICAL SCOPE:
           - What types of studies should be included?
           - What time period is relevant?
           - What geographical/cultural contexts apply?
           - What research methodologies are most relevant?
        
        4. SEARCH STRATEGY:
           - Identify key search terms and synonyms
           - Suggest Boolean search combinations
           - Recommend relevant databases/sources
           - Propose inclusion/exclusion criteria
        
        FORMAT YOUR RESPONSE AS:
        
        ## Research Questions
        1. [Primary Question]: [Clear, specific question]
           - Rationale: [Why this question is important]
           - Keywords: [List of 5-8 relevant terms]
           
        2. [Secondary Question]: [Follow same format]
        
        ## Scope Definition
        - Conceptual boundaries: [What concepts are central/peripheral]
        - Temporal scope: [Time period covered]
        - Methodological inclusion: [Types of studies included]
        - Population/context: [Who/what contexts are relevant]
        
        ## Search Strategy
        - Primary keywords: [Core terms]
        - Alternative terms: [Synonyms and variations]
        - Boolean combinations: [Suggested search strings]
        - Inclusion criteria: [What makes a source relevant]
        - Exclusion criteria: [What to filter out]
        
        Be thorough and academically rigorous in your analysis.
        """
    
    @staticmethod
    def get_literature_search_prompt(research_question: str, keywords: List[str]) -> str:
        keyword_string = ", ".join(keywords)
        return f"""
        You are conducting a systematic literature search for the research question: "{research_question}"
        
        KEYWORDS: {keyword_string}
        
        TASK: Comprehensively search the knowledge base and extract all relevant literature.
        
        SEARCH REQUIREMENTS:
        
        1. SYSTEMATIC IDENTIFICATION:
           - Search for all studies related to the research question
           - Look for both direct and indirect relevance
           - Include seminal works and recent developments
           - Consider multiple perspectives and approaches
        
        2. SOURCE CATEGORIZATION:
           For each source found, extract:
           - Title and authors
           - Publication year and type (journal, book, conference, etc.)
           - Research methodology used
           - Theoretical framework applied
           - Sample size and population (if applicable)
           - Key findings and conclusions
           - Limitations acknowledged by authors
           - Relevance to the research question (1-10 scale)
        
        3. METHODOLOGICAL DIVERSITY:
           - Include quantitative, qualitative, and mixed-methods studies
           - Consider theoretical/conceptual papers
           - Include systematic reviews and meta-analyses
           - Look for case studies and ethnographic work
        
        4. TEMPORAL COVERAGE:
           - Include foundational/seminal works
           - Emphasize recent developments (last 5-10 years)
           - Note any historical trends or evolution
        
        5. QUALITY INDICATORS:
           - Publication venue reputation
           - Citation frequency
           - Methodological rigor
           - Peer review status
        
        FORMAT YOUR RESPONSE AS:
        
        ## Literature Search Results for: "{research_question}"
        
        ### High Relevance Sources (8-10/10)
        
        **[Author(s), Year]** - "[Title]"
        - Publication: [Journal/Book/Conference]
        - Methodology: [Research approach]
        - Key Finding: [Most important result/conclusion]
        - Theoretical Framework: [If applicable]
        - Sample: [If applicable]
        - Relevance: [Why highly relevant]
        - Limitations: [Acknowledged by authors]
        
        ### Moderate Relevance Sources (5-7/10)
        [Follow same format]
        
        ### Supporting Sources (3-4/10)
        [Follow same format]
        
        ### Search Summary
        - Total sources identified: [Number]
        - Methodological distribution: [Breakdown by method]
        - Temporal distribution: [Breakdown by time period]
        - Geographic/cultural coverage: [If relevant]
        - Gaps identified: [What's missing]
        
        Be thorough and ensure academic rigor in source evaluation.
        """
    
    @staticmethod
    def get_thematic_analysis_prompt(topic: str) -> str:
        return f"""
        You are conducting a thematic analysis of literature on "{topic}".
        
        TASK: Identify, analyze, and organize major themes, patterns, and debates.
        
        ANALYTICAL FRAMEWORK:
        
        1. THEMATIC IDENTIFICATION:
           - What are the major conceptual themes?
           - What methodological patterns emerge?
           - What theoretical approaches dominate?
           - What practical applications are discussed?
        
        2. PATTERN ANALYSIS:
           - Where do researchers agree?
           - What consistent findings emerge?
           - What methodological consensus exists?
           - What theoretical convergence is apparent?
        
        3. DEBATE IDENTIFICATION:
           - What are the major controversies?
           - Where do findings contradict?
           - What methodological debates exist?
           - What theoretical conflicts are evident?
        
        4. EVOLUTION ANALYSIS:
           - How has thinking evolved over time?
           - What new directions are emerging?
           - What questions remain unresolved?
           - What paradigm shifts are occurring?
        
        5. GAP ANALYSIS:
           - What populations are understudied?
           - What contexts lack attention?
           - What methodological gaps exist?
           - What theoretical developments are needed?
        
        FORMAT YOUR RESPONSE AS:
        
        ## Thematic Analysis: {topic}
        
        ### Major Theme 1: [Theme Name]
        
        **Definition**: [Clear description of the theme]
        
        **Supporting Evidence**:
        - [Author, Year]: [Key finding/argument]
        - [Author, Year]: [Key finding/argument]
        - [Author, Year]: [Key finding/argument]
        
        **Methodological Approaches**:
        - [Method 1]: [How it's been used, by whom]
        - [Method 2]: [How it's been used, by whom]
        
        **Theoretical Perspectives**:
        - [Theory 1]: [How it's applied]
        - [Theory 2]: [How it's applied]
        
        **Internal Debates**:
        - [Controversy 1]: [Description and key positions]
        - [Controversy 2]: [Description and key positions]
        
        **Gaps Identified**:
        - [Gap 1]: [What's missing and why it matters]
        - [Gap 2]: [What's missing and why it matters]
        
        ### Major Theme 2: [Follow same format]
        
        ### Cross-Cutting Patterns
        - [Pattern 1]: [Description and significance]
        - [Pattern 2]: [Description and significance]
        
        ### Major Debates and Controversies
        - [Debate 1]: [Positions, evidence, implications]
        - [Debate 2]: [Positions, evidence, implications]
        
        ### Methodological Landscape
        - Dominant approaches: [List and analysis]
        - Emerging methods: [New developments]
        - Methodological gaps: [What's needed]
        
        ### Theoretical Development
        - Established frameworks: [Current theories]
        - Emerging perspectives: [New theoretical work]
        - Theoretical gaps: [What's missing]
        
        Ensure deep analysis that goes beyond surface-level description.
        """
    
    @staticmethod
    def get_synthesis_prompt(topic: str, themes: List[str]) -> str:
        themes_string = ", ".join(themes)
        return f"""
        You are synthesizing literature on "{topic}" to develop a comprehensive conceptual framework.
        
        IDENTIFIED THEMES: {themes_string}
        
        TASK: Create a sophisticated synthesis that integrates findings across themes.
        
        SYNTHESIS REQUIREMENTS:
        
        1. CONCEPTUAL INTEGRATION:
           - How do the themes relate to each other?
           - What overarching patterns connect different areas?
           - What unified understanding emerges?
           - How do micro and macro perspectives connect?
        
        2. THEORETICAL SYNTHESIS:
           - What theoretical frameworks best explain the phenomena?
           - How do different theories complement each other?
           - What new theoretical insights emerge?
           - What integrated model could be proposed?
        
        3. METHODOLOGICAL SYNTHESIS:
           - What do different methodological approaches reveal?
           - How do quantitative and qualitative findings converge/diverge?
           - What methodological triangulation is possible?
           - What new methodological approaches are needed?
        
        4. EMPIRICAL SYNTHESIS:
           - What robust findings emerge across studies?
           - What contextual factors influence outcomes?
           - What moderating variables are important?
           - What effect sizes or strength of relationships exist?
        
        5. PRACTICAL SYNTHESIS:
           - What implications for practice emerge?
           - What recommendations can be made?
           - What policy implications exist?
           - What implementation considerations matter?
        
        FORMAT YOUR RESPONSE AS:
        
        ## Synthesis: {topic}
        
        ### Conceptual Framework
        
        **Core Phenomenon**: [Central concept being studied]
        
        **Key Components**:
        1. [Component 1]: [Definition and role]
        2. [Component 2]: [Definition and role]
        3. [Component 3]: [Definition and role]
        
        **Relationships Between Components**:
        - [Component A] → [Component B]: [Nature of relationship]
        - [Component B] ↔ [Component C]: [Bidirectional relationship]
        
        **Moderating Factors**:
        - [Factor 1]: [How it influences the relationships]
        - [Factor 2]: [How it influences the relationships]
        
        ### Theoretical Integration
        
        **Primary Theoretical Framework**: [Main theory]
        - Strengths: [What it explains well]
        - Limitations: [What it doesn't explain]
        - Supporting evidence: [Key studies]
        
        **Complementary Theories**: [Additional frameworks]
        - [Theory 1]: [How it adds to understanding]
        - [Theory 2]: [How it adds to understanding]
        
        **Proposed Integrated Model**: [New synthesis]
        - [Description of how theories combine]
        - [Novel insights that emerge]
        
        ### Methodological Insights
        
        **Convergent Findings**: [What all methods show]
        **Divergent Findings**: [Where methods disagree]
        **Methodological Strengths**: [What works well]
        **Methodological Gaps**: [What's needed]
        
        ### Empirical Patterns
        
        **Robust Findings**: [Consistent across studies]
        **Contextual Variations**: [How context matters]
        **Effect Sizes**: [Strength of relationships]
        **Causal Mechanisms**: [How things work]
        
        ### Practical Implications
        
        **For Practitioners**: [Direct applications]
        **For Policymakers**: [Policy recommendations]
        **For Researchers**: [Research priorities]
        **For Society**: [Broader implications]
        
        ### Future Directions
        
        **Priority Research Questions**: [Most important next steps]
        **Methodological Innovations Needed**: [New approaches required]
        **Theoretical Developments Required**: [Conceptual work needed]
        
        Ensure sophisticated integration that creates new understanding.
        """
    
    @staticmethod
    def get_academic_writing_prompt(section_title: str, section_purpose: str, key_sources: List[str]) -> str:
        sources_string = "; ".join(key_sources)
        return f"""
        You are writing the "{section_title}" section of an academic literature review.
        
        SECTION PURPOSE: {section_purpose}
        KEY SOURCES TO INTEGRATE: {sources_string}
        
        WRITING REQUIREMENTS - Follow the 5 C's Framework:
        
        1. CITE: Integrate sources appropriately
           - Use proper in-text citations (Author, Year)
           - Balance direct quotes with paraphrasing
           - Ensure every major claim is supported
           - Cite primary sources when possible
        
        2. COMPARE: Identify similarities and agreements
           - "Similarly, X and Y both found..."
           - "Consistent with this finding, Z reported..."
           - "Multiple studies converge on the conclusion that..."
           - "Across different contexts, researchers have consistently observed..."
        
        3. CONTRAST: Highlight differences and disagreements
           - "However, A's findings contradict B's results..."
           - "While some studies suggest X, others indicate Y..."
           - "Methodological differences may explain why..."
           - "Cultural context appears to influence..."
        
        4. CRITIQUE: Evaluate strengths and limitations
           - "The strength of this approach lies in..."
           - "However, methodological limitations include..."
           - "While the sample size was robust, generalizability is limited by..."
           - "The theoretical framework provides insight but fails to account for..."
        
        5. CONNECT: Link to broader context and implications
           - "These findings have important implications for..."
           - "This relates to the broader theoretical debate about..."
           - "The practical significance of this research lies in..."
           - "Future research should build on these insights by..."
        
        ACADEMIC WRITING STANDARDS:
        
        **Structure Requirements**:
        - Opening: Introduce the focus and importance of this section
        - Development: Systematically compare/contrast key studies
        - Analysis: Critically evaluate the evidence
        - Synthesis: Integrate findings into coherent understanding
        - Transition: Connect to next section or overall argument
        
        **Style Requirements**:
        - Use third person academic voice
        - Employ precise, disciplinary language
        - Maintain objective, analytical tone
        - Ensure logical flow between sentences and paragraphs
        - Use varied sentence structures
        
        **Citation Requirements**:
        - In-text citations: (Author, Year) or Author (Year)
        - Multiple authors: (Smith et al., Year)
        - Direct quotes: "Quote" (Author, Year, p. X)
        - Paraphrase more than quote
        - Integrate citations smoothly into prose
        
        TARGET LENGTH: 800-1200 words
        
        FORMAT YOUR RESPONSE AS:
        
        ## {section_title}
        
        [Write the complete section following all requirements above]
        
        **Section Analysis**:
        - Key arguments presented: [List main points]
        - Sources integrated: [Count and primary contributors]
        - Critical evaluation level: [Assessment of analytical depth]
        - Connection to broader literature: [How it fits the larger picture]
        
        Write as a professional academic researcher with deep expertise in the field.
        """
    
    @staticmethod
    def get_refinement_prompt(section_content: str, refinement_type: str, feedback: str) -> str:
        refinement_instructions = {
            "improve_analysis": """
            FOCUS: Deepen the critical analysis and evaluation
            
            SPECIFIC IMPROVEMENTS:
            - Add more sophisticated critical evaluation of methodologies
            - Assess the quality and reliability of evidence more thoroughly
            - Consider alternative interpretations of findings
            - Evaluate the theoretical frameworks more critically
            - Identify subtle methodological strengths and limitations
            - Discuss validity and reliability issues
            - Consider potential biases and confounding factors
            """,
            
            "enhance_synthesis": """
            FOCUS: Improve integration and synthesis across studies
            
            SPECIFIC IMPROVEMENTS:
            - Better connect findings across different studies
            - Identify more sophisticated patterns and themes
            - Create stronger conceptual links between ideas
            - Develop more nuanced understanding of relationships
            - Integrate theoretical frameworks more effectively
            - Show how studies build upon each other
            - Create coherent narrative that synthesizes knowledge
            """,
            
            "strengthen_critique": """
            FOCUS: Strengthen critical evaluation and balanced assessment
            
            SPECIFIC IMPROVEMENTS:
            - Provide more balanced evaluation of strengths and weaknesses
            - Identify methodological limitations more clearly
            - Consider gaps and biases in the research
            - Evaluate the appropriateness of research designs
            - Assess the generalizability of findings
            - Consider ethical implications
            - Identify areas where evidence is weak or conflicting
            """,
            
            "improve_writing": """
            FOCUS: Enhance academic writing quality and clarity
            
            SPECIFIC IMPROVEMENTS:
            - Improve clarity and precision of language
            - Strengthen paragraph structure and flow
            - Enhance transitions between ideas
            - Ensure proper citation integration
            - Improve sentence variety and sophistication
            - Strengthen argumentative structure
            - Ensure academic tone and voice consistency
            """
        }
        
        instructions = refinement_instructions.get(refinement_type, "General improvement needed")
        
        return f"""
        You are refining a literature review section to improve its academic quality.
        
        REFINEMENT TYPE: {refinement_type}
        
        SPECIFIC FEEDBACK: {feedback}
        
        REFINEMENT INSTRUCTIONS:
        {instructions}
        
        ORIGINAL SECTION:
        {section_content}
        
        TASK: Revise the section to address the refinement focus while maintaining academic rigor.
        
        REQUIREMENTS:
        - Maintain all factual content and citations
        - Preserve the overall structure and argument
        - Apply the specific improvements listed above
        - Ensure the revision addresses the provided feedback
        - Maintain academic writing standards
        - Keep the word count similar (±10%)
        
        EVALUATION CRITERIA:
        - Does the revision show clear improvement in the target area?
        - Is the academic quality enhanced?
        - Are the improvements substantial and meaningful?
        - Does it maintain coherence with the broader review?
        
        FORMAT YOUR RESPONSE AS:
        
        ## Refined Section
        
        [Provide the complete refined section]
        
        ## Improvements Made
        - **Primary enhancement**: [Main improvement in focus area]
        - **Secondary improvements**: [Additional enhancements]
        - **Specific changes**: [Key modifications made]
        - **Quality indicators**: [Measures of improvement]
        
        Focus on meaningful enhancement rather than superficial changes.
        """
    
    @staticmethod
    def get_quality_assessment_prompt(review_content: str) -> str:
        return f"""
        You are conducting a quality assessment of this literature review section.
        
        REVIEW CONTENT:
        {review_content}
        
        ASSESSMENT CRITERIA:
        
        1. **COMPREHENSIVENESS** (1-10):
           - Coverage of relevant literature
           - Inclusion of diverse perspectives
           - Representation of methodological approaches
           - Temporal coverage (historical to recent)
        
        2. **CRITICAL ANALYSIS** (1-10):
           - Depth of evaluation
           - Assessment of methodological quality
           - Identification of strengths and limitations
           - Consideration of alternative interpretations
        
        3. **SYNTHESIS QUALITY** (1-10):
           - Integration across studies
           - Identification of patterns and themes
           - Coherent narrative development
           - Conceptual framework development
        
        4. **ACADEMIC WRITING** (1-10):
           - Clarity and precision
           - Appropriate academic tone
           - Proper citation integration
           - Logical structure and flow
        
        5. **METHODOLOGICAL RIGOR** (1-10):
           - Systematic approach to literature search
           - Appropriate inclusion/exclusion criteria
           - Balanced representation of evidence
           - Recognition of limitations
        
        FORMAT YOUR RESPONSE AS:
        
        ## Quality Assessment Report
        
        ### Overall Quality Score: [X/50]
        
        ### Detailed Ratings:
        - **Comprehensiveness**: [Score/10] - [Brief justification]
        - **Critical Analysis**: [Score/10] - [Brief justification]
        - **Synthesis Quality**: [Score/10] - [Brief justification]
        - **Academic Writing**: [Score/10] - [Brief justification]
        - **Methodological Rigor**: [Score/10] - [Brief justification]
        
        ### Strengths:
        - [Strength 1]: [Specific example]
        - [Strength 2]: [Specific example]
        - [Strength 3]: [Specific example]
        
        ### Areas for Improvement:
        - [Area 1]: [Specific recommendation]
        - [Area 2]: [Specific recommendation]
        - [Area 3]: [Specific recommendation]
        
        ### Priority Improvements:
        1. [Most important improvement needed]
        2. [Second priority improvement]
        3. [Third priority improvement]
        
        ### Recommendations for Enhancement:
        - **Immediate**: [Quick fixes that would improve quality]
        - **Substantial**: [More significant revisions needed]
        - **Advanced**: [Sophisticated improvements for excellence]
        
        Provide honest, constructive assessment that guides improvement.
        """

    @staticmethod
    def get_introduction_prompt(topic: str, research_questions: List[str]) -> str:
        questions_string = "\n".join([f"- {q}" for q in research_questions])
        return f"""
        You are writing the Introduction section for a literature review on "{topic}".
        
        RESEARCH QUESTIONS TO ADDRESS:
        {questions_string}
        
        INTRODUCTION REQUIREMENTS:
        
        1. **ESTABLISH CONTEXT**:
           - Define key terms and concepts clearly
           - Explain why this topic is significant and timely
           - Provide necessary background context
           - Position the topic within broader academic discourse
        
        2. **OUTLINE SCOPE**:
           - Clearly state what the review covers and what it excludes
           - Explain the boundaries of the review
           - Specify the time frame covered
           - Identify the types of sources included
        
        3. **PRESENT RESEARCH QUESTIONS**:
           - State the main research questions driving the review
           - Explain how these questions will be addressed
           - Show the logical relationship between questions
        
        4. **PREVIEW STRUCTURE**:
           - Outline how the review is organized
           - Explain the logic behind the structure
           - Guide the reader through what to expect
        
        5. **ESTABLISH PURPOSE**:
           - Clarify the aims and objectives of the review
           - Explain the intended contribution to knowledge
           - Justify why this review is needed
        
        ACADEMIC WRITING REQUIREMENTS:
        - Use engaging opening that captures attention
        - Maintain formal academic tone
        - Ensure logical progression of ideas
        - Use clear, precise language
        - Include appropriate citations to establish context
        - Target length: 400-600 words
        
        FORMAT YOUR RESPONSE AS:
        
        ## Introduction
        
        [Write the complete introduction section]
        
        This introduction should effectively set up the entire literature review and engage academic readers.
        """

    @staticmethod
    def get_conclusion_prompt(topic: str, key_findings: List[str], gaps: List[str]) -> str:
        findings_string = "\n".join([f"- {f}" for f in key_findings])
        gaps_string = "\n".join([f"- {g}" for g in gaps])
        
        return f"""
        You are writing the Conclusion section for a literature review on "{topic}".
        
        KEY FINDINGS TO SYNTHESIZE:
        {findings_string}
        
        IDENTIFIED GAPS:
        {gaps_string}
        
        CONCLUSION REQUIREMENTS:
        
        1. **SYNTHESIZE MAIN FINDINGS**:
           - Summarize the most important insights from the review
           - Highlight areas of consensus in the literature
           - Note significant debates or controversies
           - Connect findings to the original research questions
        
        2. **IDENTIFY THEORETICAL CONTRIBUTIONS**:
           - What theoretical insights emerged?
           - How do findings advance understanding?
           - What conceptual frameworks proved most useful?
        
        3. **HIGHLIGHT METHODOLOGICAL INSIGHTS**:
           - What methodological approaches were most effective?
           - What methodological limitations were common?
           - What innovations in methodology were noted?
        
        4. **DISCUSS PRACTICAL IMPLICATIONS**:
           - What are the implications for practice?
           - What recommendations can be made?
           - How can this knowledge be applied?
        
        5. **IDENTIFY FUTURE RESEARCH DIRECTIONS**:
           - What questions remain unanswered?
           - What new research is most urgently needed?
           - What methodological developments would advance the field?
        
        6. **ACKNOWLEDGE LIMITATIONS**:
           - What are the limitations of this review?
           - What sources might have been missed?
           - What biases might exist in the review process?
        
        ACADEMIC WRITING REQUIREMENTS:
        - Provide definitive closure to the review
        - Avoid introducing new information
        - Maintain authoritative, conclusive tone
        - Demonstrate the value of the review
        - Target length: 400-600 words
        
        FORMAT YOUR RESPONSE AS:
        
        ## Conclusion
        
        [Write the complete conclusion section]
        
        This conclusion should provide clear closure while opening pathways for future research.
        """


# Usage example for integration with the GraphRAG system
class EnhancedPromptManager:
    """
    Manages prompt generation for different phases of literature review
    """
    
    def __init__(self):
        self.templates = AcademicPromptTemplates()
    
    def get_phase_prompt(self, phase: str, **kwargs) -> str:
        """
        Get the appropriate prompt for a specific phase
        """
        if phase == "scoping":
            return self.templates.get_scoping_prompt(kwargs.get('topic', ''))
        elif phase == "searching":
            return self.templates.get_literature_search_prompt(
                kwargs.get('research_question', ''),
                kwargs.get('keywords', [])
            )
        elif phase == "analyzing":
            return self.templates.get_thematic_analysis_prompt(kwargs.get('topic', ''))
        elif phase == "synthesizing":
            return self.templates.get_synthesis_prompt(
                kwargs.get('topic', ''),
                kwargs.get('themes', [])
            )
        elif phase == "writing":
            return self.templates.get_academic_writing_prompt(
                kwargs.get('section_title', ''),
                kwargs.get('section_purpose', ''),
                kwargs.get('key_sources', [])
            )
        elif phase == "introduction":
            return self.templates.get_introduction_prompt(
                kwargs.get('topic', ''),
                kwargs.get('research_questions', [])
            )
        elif phase == "conclusion":
            return self.templates.get_conclusion_prompt(
                kwargs.get('topic', ''),
                kwargs.get('key_findings', []),
                kwargs.get('gaps', [])
            )
        elif phase == "refining":
            return self.templates.get_refinement_prompt(
                kwargs.get('section_content', ''),
                kwargs.get('refinement_type', ''),
                kwargs.get('feedback', '')
            )
        elif phase == "assessment":
            return self.templates.get_quality_assessment_prompt(
                kwargs.get('review_content', '')
            )
        else:
            raise ValueError(f"Unknown phase: {phase}")