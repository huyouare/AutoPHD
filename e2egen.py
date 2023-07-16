from plotgen import CodeInterpreter
from papergen_parallel import generate_paper, generate_paper_skeleton
import asyncio
import json


def run(file_path):
    async def main(file_path):
        # First generate a topic
        interpreter = CodeInterpreter()
        topic, figures = await interpreter.generate_response(
            "Given the data in a file called climate.csv, tell me up to 5 insights and generate 5 figures that can be used to write a publishable paper. Provide a short description for each figure, numbered accordingly.",
            "climate.csv")
        print("TOPIC:", topic)
        print("FIGURES:", figures)
        # Pass the figure paths to the generate_paper function
        figure_paths = []
        # Save the figures to disk
        for index, figure in enumerate(figures):
            path = f"figure_{index}.png"
            figure.save(path)
            figure_paths.append(path)

        skeleton = generate_paper_skeleton(topic)
        # Then generate a paper
        generate_paper(topic, skeleton, figure_paths)
        

    asyncio.run(main(file_path))


if __name__ == "__main__":
    async def main():
        # First generate a topic
        interpreter = CodeInterpreter()
        topic, figures = await interpreter.generate_response(
            "Given the data in a file called climate.csv, tell me up to 5 insights and generate 5 figures that can be used to write a publishable paper. Provide a short description for each figure, numbered accordingly.",
            "climate.csv")
        print("TOPIC:", topic)
        print("FIGURES:", figures)
        # Pass the figure paths to the generate_paper function
        figure_paths = []
        # Save the figures to disk
        for index, figure in enumerate(figures):
            path = f"figure_{index}.png"
            figure.save(path)
            figure_paths.append(path)

        skeleton = generate_paper_skeleton(topic)
        # Then generate a paper
        generate_paper(topic, skeleton, figure_paths)
        

    asyncio.run(main())
