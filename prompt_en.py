DRAFT_PROMPT = """
# Visual Novel Outline Writing

You are a creative screenwriter. Now, please write an outline for a first-person visual novel based on the user requirements provided below, organizing the plot by chapters and carefully planning to create a plot that meets the player's requirements. The player will play one of the characters in the first person.
For the outline content, provide the world view, character settings, character appearances, and a general plot. Do not go into specific details or character dialogues.

Write a plot of no less than 15 chapters.

## Setting Information

Give the basic settings of all the characters appearing in the plot, including character names, background stories, personality traits, appearance characteristics (hairstyle, hair color, eye color, body shape, etc.), and clothing (top and bottom styles, colors, accessories, etc.).

## Plot Branches

Arrange plot branches in the outline, allowing players to make choices in different branches and leading to different endings. This work should have a tree-like line structure, not a single main line.
If an option leads to a different branch, you need to clearly indicate the name of the branch to avoid confusion in the chapter structure.
If some chapter(s) belong to a specific branch, you need to clearly indicate the branch it belongs to after the chapter name.

## Precautions

Since this is a visual novel with a pre-arranged plot, do not design customizable content for players, nor design system mechanisms that require calculation, such as favorability, fatigue, or economic systems. Impress players only through the plot.
Each chapter should have a name, and the chapter name and chapter content should be given in the outline.
You need to choose a suitable name for this visual novel.
Organize the content using markdown syntax to facilitate subsequent tool parsing.
Only output the outline content, without any other information, and no need to discuss it further with me.
Write all content in Chinese.

The theme (and supplementary notes) provided to you by the user: {game_theme}
"""

PARSE_DRAFT_PROMPT = """
The user will provide you with an outline of a visual novel, and you should parse it into JSON format for subsequent program processing.
The returned JSON format should include the following:
- game_name: The name of the game.
- characters: All the characters that appear, including the character name, the character name in the Ren'Py engine, background story, personality traits, and appearance characteristics.
- player_character: The character played by the player, which is one of the characters.
- chapters: All chapters, including chapter name, branch line to which the chapter belongs, and chapter content.
- remarks: Any other content that needs to be explained, such as story background, settings, etc.

Example:
{
    "game_name": "Game Name",
    "characters": [
        {
            "name": "Character 1",
            "renpy_name": "character1",
            "background": "Character 1's background story",
            "personality": "Character 1's personality traits",
            "features": "Character 1's appearance characteristics"
        },
        {
            "name": "Character 2",
            "renpy_name": "character2",
            "background": "Character 2's background story",
            "personality": "Character 2's personality traits",
            "features": "Character 2's appearance characteristics"
        }
    ],
    "player_character": "Character 1",
    "chapters": [
        {
            "name": "Blooming Lies",
            "branch": "Main Route",
            "content": "Content of this chapter"
        },
        {
            "name": "Trajectory Selection",
            "branch": "Route A",
            "content": "Content of this chapter"
        }
    ],
    "world_view": "Game's worldview",
    "remarks": "Other content that needs to be explained"
}

Do not modify the names of the Keys in the example, just fill in the corresponding Value.
"""

GENERATE_CHAPTER_PROMPT = """
Craft a detailed plot for {chapter_name} based on the following visual novel plot outline, incorporating creativity, character dialogue, scene descriptions, detailed descriptions, and event development. Write the plot as comprehensively as possible.

Ensure dialogues between characters last for a sufficient number of turns, avoiding abrupt endings within just a few lines.

The plot's logic should be continuous and natural, avoiding jumps. Narration is an essential part of visual novel plots; use narration or characters' inner monologues when necessary to provide supplementary explanations, making it clear to the player what is happening.

Pay attention to the transitions between scenes, explaining changes in scenery promptly to avoid abrupt scene switches.

Refer to the content of previous chapters (if any), paying attention to foreshadowing and callbacks.

Use metaphors sparingly.

When writing, maintain the personality traits and backstories of the main characters, ensuring they align with the outline.

Handle the plot branches specified in the outline carefully, ensuring that the plot diverges differently when making choices in different branches.

The outline content will be provided in a structured JSON format, but you should write in plain text.

Only output information related to the plot, without asking for my opinions or discussing it with me.

Write all content in Chinese.

Outline content:
{draft_content}
"""

GENERATE_CHAPTER_SCRIPT_PROMPT = r"""
Rewrite the specific script of {chapter_name} into Ren'Py script, according to the visual novel plot outline below, to adapt to the production of visual novels.
Only output the script content, without asking for my opinion or discussing it with me.
In this visual novel, the player plays one of the characters in the first person. The system should refer to the player in the second person "you".
[Important] Do not miss any dialogues and details in the plot, you should make the logic of the script natural and smooth, and avoid generating logically confusing or jumping scripts.
Narration is an important part of the visual novel plot. Supplement and explain it with narration or character's inner monologue when necessary, so that players understand what is happening now. Do not delete the existing content in the script. Do your best to write a coherent and immersive script performance.
You can fabricate any image and music materials needed in the script, but be careful to use all ASCII characters as material names, and do not use Chinese.
You should arrange some full-screen CGs in appropriate places to improve the overall look and feel of the work.
The material names follow the following conventions:
- Use the `show` statement to display character portraits
- Use the `scene` statement to display background images. Background images should start with `bg`
- Use `play music` to play background music.
- Use `play sound` to play sound effects.
- Use `stop music` to stop background music
[Important] When displaying any character portrait through the script, you need to set a zoom of 0.5 times through the zoom keyword so that the character portrait is displayed completely:
```renpy
show ivan smile at right with dissolve:
    zoom 0.5
```
Avoid using `flash` and `spiral` effects, they are not supported by Ren'Py.
Character portraits should have expression modifiers, such as happy, smile, worried, etc., in order to better express the character's emotions.
Allow parentheses to indicate the speaker's actions in the dialogue.
Do not scale background images.
When displaying pictures or playing sounds, use the name of the material directly, do not carry the path, and do not specify the file format:
```renpy
show mary happy
play music opening_song
```
[Important] Pay attention to following the Ren'Py character names specified in the outline. If characters not mentioned in the outline appear in the script (usually minor characters such as NPCs), you need to define this character at the beginning of the current chapter's script. Do not define characters that already exist in the outline.
Each chapter of the plot should have a label, for example, the first chapter is chapter1, and the second chapter is chapter2. There must be no duplicate labels in the entire game.
At the end of each chapter, if the game does not end early, jump to the next chapter through the `jump` statement. Do not define the label of the next chapter at the end of the script of this chapter!
If the current chapter is the last chapter, end the game with the `return` statement.
If you need to insert a percent sign \% in the script, you need to escape it: \%

Outline content:
{draft_content}

【{chapter_name}】Specific plot:
{chapter_content}
"""

GENERATE_SPRITE_SD_PROMPT = """
You are a professional Stable Diffusion (SD) prompt writer. Now, please direct an SD model to generate some images for game character portraits.
Write all the necessary prompts based on the character settings and Ren'Py script provided to you. Any `show` statements used in the script to display images are considered portraits and require prompts to be generated. Note that the part after the `at` keyword is not part of the image name.
Output a list of prompts in JSON format. The JSON should contain an array, with each element in the array containing the following parts:
- character_renpy_name: The name of the character in Ren'Py.
- image_name: The name of the image. You must strictly adhere to the name in the script and do not mix underscores and spaces. If underscores are used in the script, the generated image name should also use underscores. The same applies to spaces.
- prompt: The list of prompts.

You should organize the prompts using lowercase **English** words or sentences, separated by commas ",". You only need to output positive prompts, not negative prompts.
Note that when writing character portrait prompts, do not describe the environment outside of the character.
Pay attention to writing prompts that reflect the worldview characteristics in the script content.
The following prompts are required: white background, simple background, cowboy shot, standing, looking at viewer
The age range of the character can be controlled by prompts such as toddler, teenager, mature male/female, elderly.
If the character setting includes a description of the feet or shoes, you should ignore them, because including these contents in the prompt will make it difficult for the SD model to generate images that meet the "cowboy shot" requirement.

Here are some example prompts for your reference:

1girl, white background, standing, black hair, brown eyes, black round glasses, blue dress, hair ornament, light smile, looking at viewer, younger sister, cowboy shot, best quality, masterpiece, highres

1boy, cowboy shot, white background, iron hammer, blacksmith, rugged, practical, left hand wearing copper ring, standing high detail, masterpiece, best quality, amazing quality

Example output:
[
  {
    "character_renpy_name": "ellen",
    "image_name": "ellen happy",
    "prompt": "(omitted)"
  },
  {
    "character_renpy_name": "ellen",
    "image_name": "ellen anxious",
    "prompt": "(omitted)"
  },
  {
    "character_renpy_name": "bob",
    "image_name": "ellen angry",
    "prompt": "(omitted)"
  }
]
"""

SELECT_BEST_SPRITE_PROMPT = """
The following Stable Diffusion prompts generated several images:
{sd_prompts}

Now, please select the image that is most suitable as a character illustration for a visual novel.
Requirements: No missing limbs, transparent background with no clutter, good overall visual quality.
Output the data in JSON format, indicating the index of the most suitable image. Do not provide any explanation of the result. For example:

{{
    "best": 2
}}
"""

GENERATE_BACKGROUND_SD_PROMPT = """
you are a professional Stable Diffusion (SD) prompt writer. below, please instruct an SD model to generate some images for game backgrounds.
write all necessary prompts based on the Ren'Py script provided. images that start with `bg` in the script are background images, and prompts need to be generated for them.
output a list of prompts in JSON format. the JSON should contain an array, with each element in the array including the following parts:
- image_name: the name of the image. strictly follow the names in the script, do not mix underscores and spaces. if the script uses underscores, the generated image names should also use underscores. the same applies to spaces.
- prompt: the list of prompts.

you should organize the prompts using lowercase **english** words or sentences, separated by commas ",". you only need to output positive prompts, not negative prompts.
generally, use "background" to indicate that the image to be generated is a background image.
pay attention to the characteristics of the world view reflected in the script when writing prompts.
note that when writing background prompts, do not describe characters or other foreground elements. generally, there should be no characters in background images.

here are some sample prompts for your reference:

no humans, night, neon lights, street, lamp, cars, best quality, masterpiece, highres

no humans, forest, blue sky, river, flower, grass, bush, plant, best quality, masterpiece, highres

background, cafe, table, chair, window, waitress, best quality, masterpiece, highres

example output:
[
  {
    "image_name": "bg cafe",
    "prompt": "(omitted)"
  },
  {
    "image_name": "bg forest",
    "prompt": "(omitted)"
  }
]
"""

SELECT_BEST_BACKGROUND_PROMPT = """
The following Stable Diffusion prompts generated several images:
{sd_prompts}

Now, please select the image that is most suitable as a background for a visual novel from these images. Output the data in JSON format, indicating the number of the most suitable image. Do not provide any explanation for the result. For example:

{{
    "best": 2
}}
"""

GENERATE_CG_SD_PROMPT = """
you are a professional stable diffusion (sd) prompt writer. below, please direct an sd model to generate some full-screen cg images for a game.
write all necessary prompts based on the ren'py script provided. in the script, all images starting with `e` are full-screen cg images that require prompts.
output the list of prompts in json format. the json should contain an array, with each element in the array including the following parts:
- image_name: the name of the image. strictly follow the names in the script, do not mix underscores and spaces.
- prompt: the list of prompts.
if no cg images are used in the script, return an empty array.

you should organize the prompts using all lowercase words or sentences, separated by commas ",". only output positive prompts, do not output negative prompts.
generally, cg images should include complete scenes and characters, with highly dramatic and richly detailed visuals.

here are some prompt examples for your reference:

1boy, 1girl, cafe, couple, sitting, coffee, romantic scene, warm lighting, detailed scene, emotional moment, best quality, masterpiece, highres

1girl, looking at viewer, reaching out, forest, blue sky, river, flower, grass, bush, plant, emotional, dramatic lighting, character portrait, best quality, masterpiece, highres

example output:
[
  {
    "image_name": "e old_photo",
    "prompt": "(omitted)"
  },
  {
    "image_name": "e violet_petals",
    "prompt": "(omitted)"
  }
]
"""

SELECT_BEST_CG_PROMPT = """
The following Stable Diffusion prompts generated several images:
{sd_prompts}

Now, please select the image most suitable for use as a full-screen CG in a visual novel.
Criteria: Complete composition, rich scene and character details, expressive emotions, and high overall visual quality.
Output the data in JSON format, indicating the number of the most suitable image. Do not provide any explanation for the result. For example:

{{
    "best": 2
}}
"""

GENERATE_MUSIC_PROMPT = """
You are a professional Stable Audio prompt writer. Below, please analyze the provided Ren'Py script and write prompts for generating background music.
Based on the `play music` commands in the Ren'Py script provided to you, write all necessary music prompts.
Output the prompts in JSON format. The JSON should contain an array, where each element of the array includes the following parts:
- audio_name: The name of the music. Strictly follow the names used in the script, do not mix underscores and spaces. If the script uses underscores, the generated audio name should also use underscores. The same applies to spaces.
- prompt: A list of prompts, used to generate the music.

Describe the prompts from multiple dimensions, with each dimension separated by a vertical bar. Here are all the optional dimensions and corresponding examples:

## Format
- Solo
- Band
- Orchestra
- Chorus
- Duet

## Genre
- Rock
- Pop
- Hip Hop
- Indie
- Foley
- RnB

## Sub-genre
- Drum loops
- Electric guitar
- Pop Music
- Chillout
- Ambient
- Techno

## Instruments
- Piano
- Drum machine
- Synthesizer
- Snare drum
- Keyboard
- Organ
- Strings
- Percussion
- Ukulele

## Moods
- Dramatic
- Inspiring
- Magical
- Uplifting
- Driving
- Animated
- Tag
- Atmospheric
- Happy

## Styles
- Film Instrumental
- 2000s
- 1960s
- Dance
- Video Games
- High Tech
- Sci-Fi

## Tempo
- Medium
- Slow
- Building
- Fast
- Very Fast

## BPM
- 180 (e.g. Drum and bass)
- 140 (e.g. Dubstep)
- 120 (e.g. Techno/trance)
- 100 (e.g. House)
- 180 (e.g. Hip-hop)
- 60 (e.g. Dub)

Example output:
[
  {
    "audio_name": "rock",
    "prompt": "Genre: Rock | Subgenre: Pop Rock, Indie Rock | Instruments: Guitar, Drum Kit, Bass, Electric Guitar | Moods: Driving, Strong, Edgy | Tempo: Medium"
  },
  {
    "audio_name": "epic",
    "prompt": "Format: Orchestra | Subgenre: Hollywood Orchestral Epic | Instruments: Strings, Drum Kit, Electric Bass, Choir, String Section, Flute, Harp, | Moods: Atmospheric, Spacious, cinematic, Inspiring, Beautiful | Styles: Recording, Auditorium, Film Instrumental | Tempo: Medium"
  }
]

If no music is used in the script, return an empty array.
"""

GENERATE_SFX_PROMPT = """
you are a professional stable audio prompt writer. below, please analyze the provided ren'py script and write prompts for generating sound effects.
based on the `play sound` instructions that appear in the ren'py script you are given, write all necessary audio prompts.
output the list of audio prompts in json format. the json should contain an array, where each element in the array includes the following parts:
- audio_name: the name of the sound effect. strictly follow the names used in the script, do not mix underscores and spaces. if the script uses underscores, the generated audio name should also use underscores. the same applies to spaces.
- prompt: a list of prompts used to generate the sound effect.

you should organize the prompts using all lowercase **english** words or sentences, separated by commas ",". the prompts should describe the characteristics, source, intensity, etc., of the sound.
pay attention to writing prompts that reflect the characteristics of the scenario described in the script content.

here are some example prompts for your reference:

door creaking open, wooden, slow, spooky, haunted house

glass breaking, shattering, crash, debris falling, impact

footsteps on wooden floor, walking, indoor, medium pace, single person

example output:
[
  {
    "audio_name": "door_creak",
    "prompt": "door creaking open, wooden, slow, spooky, haunted house",
  },
  {
    "audio_name": "glass_break",
    "prompt": "glass breaking, shattering, crash, debris falling, impact",
  }
]

if the script does not use any sound effects, return an empty array.
"""

EVALUATE_IMAGE_PROMPT = """
Please evaluate if the following image meets the requirements:
1. Image type: {mode} (could be "sprite" character sprite, "background" image, or "cg" scene)
2. Generation prompts used: {sd_prompts}
3. Reference script content:
{script_content}
4. Reference outline information:
{outline_content}
5. Requirements:
   - For character sprites (sprite): no missing limbs, clean background, matching character design, good overall visual quality, consistent with character description in the script
   - For background images: appropriate scene, no characters, consistent with story setting and environment described in the script
   - For CG images: complete composition, rich scene and character details, expressive emotions, good overall visual quality, matching the story situation in the script

Please answer the following questions:
1. Does the image meet the requirements? (yes/no)
2. Is the image consistent with the descriptions in the script and outline? (yes/no)
3. What specific issues exist? (if any)
4. How should the current prompt be modified to get better results?

Please return the result in JSON format:
{{
    "acceptable": true/false,  // Whether the image is acceptable
    "issues": ["issue1", "issue2", ...],  // List of existing issues
    "optimized_prompt": "optimized prompt"  // Improved prompt
}}
"""

SCRIPT_VALIDATION_PROMPT = r"""
Please parse the following Ren'Py Lint output and extract all errors and their related information.
The output should be a JSON array, with each error containing the following fields:
- file: The file path where the error occurred
- line: The line number where the error occurred (if available)
- description: A short description of the error
- error_type: The type of error (e.g., syntax error, duplicate label definition, etc.)

Lint output content:
{lint_content}

Just return a valid JSON array, without any other explanatory text.
"""

SCRIPT_FIX_PROMPT = r"""
Please fix the issues in the following Ren'Py script. Common issues include:
1. Missing assets. In this case, you should remove the references to the missing assets from the script.
2. Problems caused by the percent sign `%`. In this case, you should use `%%` to escape the percent sign.
3. Undefined characters. In this case, you can define the character at the very beginning of the script.
4. The effect attached to the `with` keyword is undefined, such as `flash`. In this case, you should replace it with another effect, such as `fade`.

File: {file_name}

Detected errors:
{error_descriptions}

Current file content:
```rpy
{file_content}
```

Please provide the complete fixed script content, only return the fixed script code, do not add any instructions or explanations, and do not return the original code.
"""
