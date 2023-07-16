from plotgen import CodeInterpreter
from papergen_parallel import generate_paper, generate_paper_skeleton
import asyncio
import json

if __name__ == "__main__":
    async def main():
        # First generate a topic
        interpreter = CodeInterpreter()
        topic, figures = await interpreter.generate_response(
            "Given the data in a file called climate.csv, tell me up to 5 insights and generate 3 figures that can be used to write a publishable paper. Provide a short description for each figure, numbered accordingly.",
            "climate.csv")
        print("TOPIC:", topic)
        print("FIGURES:", figures)
        # Pass the figure paths to the generate_paper function
        figure_paths = [figure.name for figure in figures]

        skeleton = generate_paper_skeleton(topic)
        # Then generate a paper
        generate_paper(topic, skeleton, figure_paths)
        # # Parse the TOC from skeleton
        # toc = skeleton.split("SECTIONS:")[1]
        # print("TOC:", toc)
        # toc = json.loads(toc)
        # print(toc)

        # figures = []
        # output = ""
            
        #     print("PROMPT:", prompt)
        #     output, figurse = await interpreter.generate_response(prompt, "climate.csv")
        #     print("OUTPUT:", output, "Figure:", figures)
        #     # figures.append((output, figure))

        

    asyncio.run(main())
