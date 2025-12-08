import pprint
from neo4j import GraphDatabase
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from get_neo4j_driver import get_neo4j_driver

def get_recommendations_for_job_description(
        job_description: str,
        student_id: int
) -> str:

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    chat_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Get Neo4j driver
    neo4j_driver = get_neo4j_driver()

    semester_name = "Spring"
    year_value = 2026

    user_query = f"Suggest courses that are a good fit for a course with the description : {job_description} offered in {semester_name} {year_value}."

    query = {
        "job_description": job_description,
        "semester": semester_name,
        "year": year_value
    }

    # creating embedding for the job_description to run semantic search
    query_embedding = embeddings.embed_query(query['job_description'])

    print("\nUser Query Embedding:")
    pprint.pprint(query_embedding)

    semantic_query = """
        CALL db.index.vector.queryNodes('course_description_chunks', 5, $query_embedding) 
        YIELD node AS chunk, score
        MATCH (chunk)-[:PART_OF]->(course:Course)<-[:OFFERING_OF]-(co:CourseOffering)
        WHERE co.CourseOfferingSemester = $semester 
        AND co.CourseOfferingYear = $year
        
        // Get prerequisites with full details
        OPTIONAL MATCH (course)-[:REQUIRES]->(prereq:Course)
        
        // Collect prerequisites with their info
        WITH course, co, score, chunk,
            collect(DISTINCT {
                courseID: prereq.CourseID,
                subjectCode: prereq.SubjectCode,
                courseNumber: prereq.CourseNumber,
                description: prereq.CourseDescription
            }) AS prerequisites
        
        RETURN
            course.CourseID AS courseID,
            course.Title AS courseTitle,
            course.SubjectCode AS subjectCode,
            course.CourseNumber AS courseNumber,
            course.CourseDescription AS courseDescription,
            co.CourseOfferingSemester AS semester, 
            co.CourseOfferingYear AS year,
            co.CourseOfferingID AS courseOfferingID,
            score,
            chunk.text AS evidence,
            CASE WHEN size(prerequisites) > 0 
                THEN prerequisites 
                ELSE [] 
            END AS prerequisites
        ORDER BY score DESC
    """

    try:
        with neo4j_driver.session() as session:
            result = session.run(semantic_query, query_embedding=query_embedding, semester=query['semester'], year=query['year'])
            semantic_results = [record.data() for record in result]
    except Exception as e:
       print(f"Error querying Neo4j: {e}")
       return None
    finally:
        neo4j_driver.close()
    
    pprint.pprint(semantic_results)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are an expert academic advisor. Your task is to analyze the provided course data
                and suggest the best recommended courses based on a user's query.
                
                Guidelines:
                - Use only the provided context. Do not make up information.
                - Summarize why each course is a good fit, citing specific evidence from the course description.
                - Consider any listed prerequisites when making recommendations.
                - For each recommended course, provide an enrollment link using this format:
                  http://localhost:8000/enroll_student_in_course_offering/?studentID={student_id}&courseOfferingID={{courseOfferingID}}
                  Replace {{courseOfferingID}} with the actual CourseOfferingID from the context.
                - Present results in a clear, professional format with clickable links.
                """
            ),
            (
                "human",
                """
                Student ID: {student_id}
                
                User Query:
                {user_query}

                Retrieved Context:
                {context}
                
                Please provide your course recommendations with enrollment links.
                """
            ),
        ]
    )

    # Define the RAG pipeline
    chain = prompt | chat_llm
    response = chain.invoke({
        "student_id": student_id,
        "user_query": user_query,
        "context": semantic_results
    })

    return response.content