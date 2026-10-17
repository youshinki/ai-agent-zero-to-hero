from crewai import Crew
from tasks import research_task, writing_task, review_task
from agents import researcher, writer, reviewer

if __name__ == "__main__":
    topic = input("请输入报告主题：")

    crew = Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        verbose=True
    )

    result = crew.kickoff(inputs={"topic": topic})

    print("\n===== 最终报告 =====")
    print(result)
