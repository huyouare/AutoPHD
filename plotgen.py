from codeinterpreterapi import CodeInterpreterSession
from codeinterpreterapi.schema.file import File


class CodeInterpreter():
    def __init__(self):
        self.session = CodeInterpreterSession()

    async def start(self):
        await self.session.astart()

    async def generate_response(self, query, file_path):
        print("Creating file...")
        f = File.from_path("/Users/jessehu/code/AutoPHD/" + file_path)
        print("FILE:", f.content)
        output = await self.session.generate_response(query, files=[f])
        print("AI: ", output.content)

        if output.files and len(output.files) > 0:
            for f in output.files:
                f.show_image()
            return output.content, output.files

        return output.content, None


async def main():
    # start a session
    print("Starting session...")
    session = CodeInterpreterSession()
    await session.astart()

    print("Creating file...")
    f = File.from_path("/Users/jessehu/code/AutoPHD/climate.csv")
    print("FILE:", f.content)

    # generate a response based on user input
    output = await session.generate_response(
        "Given the data in a file called climate.csv, tell me up to 5 insights that can be used to write a publishable paper.",
        files=[f]
    )
    # show output image in default image viewer
    if output.files and len(output.files) > 0:
        file = output.files[0]
        file.show_image()

    # show output text
    print("AI: ", output.content)

    # terminate the session
    await session.astop()
    

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
