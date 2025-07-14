DRAFT_PROMPT = """
# 视觉小说大纲撰写

你是一位富有创造力的剧本家。现在，请你根据后文提供给你的用户要求，编写一个第一人称视觉小说的大纲，以章节为单位组织剧情，通过精心的策划来编写满足玩家要求的剧情。玩家将以第一人称扮演其中一名角色。
对于大纲内容，给出世界观、角色设定和角色登场情况，以及大致的剧情。不要具体到细节描写或人物对话。

编写不少于 15 章的剧情。

## 设定信息

给出剧情中所有登场角色的基本设定，包括角色名称、背景故事、性格特点、外貌特征（发型、发色、瞳色、体型等）、衣着（上下衣款式、颜色，饰品等）。

## 剧情分支

在大纲中安排剧情分支，允许玩家在不同的分支中做出选择，并导向不同的结局。此作品应当具有树形线路结构，而不是单一主线。
如果某个选项导向了不同的分支，那么你需要明确指出导向分支的名字，从而避免章节结构产生混乱。
如果某个（某些）章节属于某个特定的分支，那么你需要在章节名称后面明确指出它所属的分支。

## 注意事项

因为这是一个剧情事先安排好的视觉小说，所以不要设计可供玩家自定义的内容，也不要设计好感度、疲劳值、经济系统等需要计算的系统机制。仅通过剧情来打动玩家。
每个章节应当有一个名称，并且在大纲中给出章节名称和章节内容。
你需要为这个视觉小说取一个合适的名字。
通过 markdown 语法组织内容，从而便于后续工具的解析。
仅输出大纲内容，无需包含任何其他信息，不必与我进一步讨论。
使用中文编写全部内容。

用户提供给你的主题（及补充说明）：{game_theme}
"""

PARSE_DRAFT_PROMPT = """
用户将向你提供一个视觉小说的大纲，请你将其解析为JSON格式，以便后续的程序处理。
返回的JSON格式应包含以下内容：
- game_name: 游戏的名称。
- characters: 所有的登场角色，包括角色名称、在Ren'Py引擎中的角色名、背景故事、性格特点和外貌特征。
- player_character: 玩家扮演的角色，是characters中的一个角色。
- chapters: 所有的章节，包括章节名称、章节所属的分支线路、章节内容。
- remarks: 任何其他需要说明的内容，例如故事背景、设定等。

示例：
{
    "game_name": "游戏名称",
    "characters": [
        {
            "name": "角色1",
            "renpy_name": "character1",
            "background": "角色1的背景故事",
            "personality": "角色1的性格特点",
            "features": "角色1的外貌特征"
        },
        {
            "name": "角色2",
            "renpy_name": "character2",
            "background": "角色2的背景故事",
            "personality": "角色2的性格特点",
            "features": "角色2的外貌特征"
        }
    ],
    "player_character": "角色1",
    "chapters": [
        {
            "name": "绽放的谎言",
            "branch": "主线路",
            "content": "此章节的内容"
        },
        {
            "name": "轨迹选择",
            "branch": "线路A",
            "content": "此章节的内容"
        }
    ],
    "world_view": "游戏的世界观",
    "remarks": "其他需要说明的内容"
}

不要修改示例中 Key 的名称，只需填写对应的 Value。
"""

GENERATE_CHAPTER_PROMPT = """
针对以下的视觉小说剧情大纲内容，发挥创造力，编写【{chapter_name}】的具体剧情，包括角色对话、场景描写、细节描写、事件发展等。尽你所能地编写详细的剧情。
角色之间的对话需要持续一定轮数，不要使对话在短短几行内结束。
剧情的逻辑应当连续自然，不要产生跳跃。旁白是视觉小说剧情的重要组成部分，在必要时通过旁白或角色内心独白来补充说明，使玩家明白现在正在发生什么事情。
注意做好场景之间的衔接，及时交代场景的变化，不要使场景切换显得突兀。
注意参考先前章节的内容（如果有），注意前后呼应。
谨慎地使用比喻。
在编写时，注意保留主要角色的性格特点和故事背景，使其与大纲相符。
注意处理大纲中指定的剧情分支，确保在不同的分支中做出选择时，剧情走向有所不同。
大纲内容将以结构化的JSON格式给出，但你应当撰写纯文本。
仅输出与剧情有关的信息，无需征求我的意见或与我讨论。
使用中文编写全部内容。

大纲内容：
{draft_content}
"""

GENERATE_CHAPTER_SCRIPT_PROMPT = r"""
针对以下的视觉小说剧情大纲内容，将【{chapter_name}】的具体剧本改写为 Ren'Py 脚本，以适配视觉小说的制作。
仅输出脚本内容，无需征求我的意见或与我讨论。
在这个视觉小说中，玩家以第一人称扮演其中一名角色。系统应当通过第二人称“你”来称呼玩家。
【重要】不要遗漏剧情中的任何对话和细节，你应当使脚本的逻辑自然流畅，避免产生逻辑混乱或跳跃的脚本。
旁白是视觉小说剧情的重要组成部分，在必要时通过旁白或角色内心独白来补充说明，使玩家明白现在正在发生什么事情。不要删去剧本中已有的内容。尽你所能编写连贯且沉浸的脚本演出。
你可以杜撰脚本中需要的任何图片和音乐素材，但要注意使用全ASCII字符作为素材名，不要使用中文。
你应当在合适的地方安排一些全屏幕CG，从而提升作品的整体观感。
素材名称遵循以下约定：
- 通过 `show` 语句展示角色立绘
- 通过 `scene` 语句展示背景图片。背景图片应当以 `bg` 开头
- 通过 `play music` 播放背景音乐。
- 通过 `play sound` 播放音效。
- 通过 `stop music` 停止背景音乐
【重要】在通过脚本显示任何角色立绘时，都需要通过zoom关键字设定0.5倍的缩放，从而使角色立绘完整显示:
```renpy
show ivan smile at right with dissolve:
    zoom 0.5
```
避免使用 `flash` 和 `spiral` 效果，它们不被 Ren'Py 所支持。
角色立绘应当带有表情修饰词，例如happy、smile、worried等，以便更好地表现角色的情绪。
允许在对话中通过括号来表示说话人的动作。
不要对背景图片进行缩放。
在展示图片或播放声音时，直接使用素材的名称，不要携带路径，也不要指定文件格式：
```renpy
show mary happy
play music opening_song
```
【重要】注意遵循大纲中指定的Ren'Py角色名称。如果脚本中出现了大纲中未提及的角色（通常为NPC等次要角色），你需要在当前章节的脚本开头处定义此角色。不要定义大纲中已有的角色。
剧情的每章应当有一个标签，例如，第一章是 chapter1，第二章是 chapter2。整个游戏中不得出现重名的标签。
在每章结束时，如果游戏没有提前结束，就通过 `jump` 语句跳转到下一章。不要在本章脚本的最后定义下一章的标签！
如果当前章是最后一章，则通过 `return` 语句结束游戏。
如果脚本中需要插入百分号%，你需要对其进行转义：\%

大纲内容：
{draft_content}

【{chapter_name}】的具体剧情：
{chapter_content}
"""

GENERATE_SPRITE_SD_PROMPT = """
你是一位专业的 Stable Diffusion (SD) 提示词撰写员。下面，请你指挥一个 SD 模型生成一些用于游戏角色立绘的图片。
根据提供给你的角色设定和Ren'Py脚本撰写所有需要的提示词。脚本中使用 `show` 语句展示的均算作立绘，需要生成提示词。注意，at关键字以及之后的部分不是图片名称的一部分。
输出JSON格式的提示词列表。JSON应当包含一个数组，数组中的每个元素包含以下几个部分：
- character_renpy_name: 角色在Ren'Py中的名称。
- image_name: 图片的名称。需要严格遵守脚本中的名称，不要混用下划线和空格。脚本中使用下划线时，生成的图片名称也应使用下划线。空格亦然。
- prompt: 提示词列表。

你应该用全小写的**英文**词语或句子来组织提示词，并用逗号","分隔它们。你只需要输出正向提示词，不要输出反向提示词。
注意，在撰写角色立绘提示词时，不要描述角色以外的环境部分。
注意根据脚本内容反映的世界观特点撰写提示词。
以下提示词是必须使用的: white background, simple background, cowboy shot, standing, looking at viewer
可通过 toddler、teenager、mature male/female、elderly 等提示词控制角色的年龄段。
如果角色设定中包含对脚部或鞋子的描写，你应当忽略它们，因为在提示词中包含这些内容会导致 SD 模型难以生成满足“cowboy shot”要求的图像。

下面是一些提示词示例，供你参考：

1girl, white background, standing, black hair, brown eyes, black round glasses, blue dress, hair ornament, light smile, looking at viewer, younger sister, cowboy shot, best quality, masterpiece, highres

1boy, cowboy shot, white background, iron hammer, blacksmith, rugged, practical, left hand wearing copper ring, standing high detail, masterpiece, best quality, amazing quality

示例输出：
[
  {
    "character_renpy_name": "ellen",
    "image_name": "ellen happy",
    "prompt": "(略)"
  },
  {
    "character_renpy_name": "ellen",
    "image_name": "ellen anxious",
    "prompt": "(略)"
  },
  {
    "character_renpy_name": "bob",
    "image_name": "ellen angry",
    "prompt": "(略)"
  }
]
"""

SELECT_BEST_SPRITE_PROMPT = """
以下的 Stable Diffusion 提示词生成了若干张图片：
{sd_prompts}

现在，请你从这些图片中挑选出最适合作为视觉小说角色立绘的一张。
要求：无肢体缺失、背景透明无杂物、整体视觉质量好。
输出JSON格式数据，在其中指出最合适图片的序号。不要对结果进行任何解释。例如：

{{
    "best": 2
}}
"""

GENERATE_BACKGROUND_SD_PROMPT = """
你是一位专业的 Stable Diffusion (SD) 提示词撰写员。下面，请你指挥一个 SD 模型生成一些用于游戏背景的图片。
根据提供给你的Ren'Py脚本撰写所有需要的提示词。脚本中出现的以 `bg` 开头的图片都是背景图，需要生成提示词。
输出JSON格式的提示词列表。JSON应当包含一个数组，数组中的每个元素包含以下几个部分：
- image_name: 图片的名称。需要严格遵守脚本中的名称，不要混用下划线和空格。脚本中使用下划线时，生成的图片名称也应使用下划线。空格亦然。
- prompt: 提示词列表。

你应该用全小写的**英文**词语或句子来组织提示词，并用逗号","分隔它们。你只需要输出正向提示词，不要输出反向提示词。
一般来说，应该使用"background"，从而表明要生成的图片是一张背景图。
注意根据脚本内容反映的世界观特点撰写提示词。
注意，在撰写背景提示词时，不要描述人物或其他前景部分。一般背景图中不应有人物出现。

下面是一些提示词示例，供你参考：

no humans, night, neon lights, street, lamp, cars, best quality, masterpiece, highres

no humans, forest, blue sky, river, flower, grass, bush, plant, best quality, masterpiece, highres

background, cafe, table, chair, window, waitress, best quality, masterpiece, highres

示例输出：
[
  {
    "image_name": "bg cafe",
    "prompt": "(略)"
  },
  {
    "image_name": "bg forest",
    "prompt": "(略)"
  }
]
"""

SELECT_BEST_BACKGROUND_PROMPT = """
以下的 Stable Diffusion 提示词生成了若干张图片：
{sd_prompts}

现在，请你从这些图片中挑选出最适合作为视觉小说背景图片的一张。输出JSON格式数据，在其中指出最合适图片的序号。不要对结果进行任何解释。例如：

{{
    "best": 2
}}
"""

GENERATE_CG_SD_PROMPT = """
你是一位专业的 Stable Diffusion (SD) 提示词撰写员。下面，请你指挥一个 SD 模型生成一些用于游戏全屏幕 CG 的图片。
根据提供给你的Ren'Py脚本撰写所有需要的提示词。脚本中出现的以 `e` 开头的图片名称都是全屏幕 CG 图，需要生成提示词。
输出JSON格式的提示词列表。JSON应当包含一个数组，数组中的每个元素包含以下几个部分：
- image_name: 图片的名称。需要严格遵守脚本中的名称，不要混用下划线和空格。
- prompt: 提示词列表。
如果脚本中没有使用任何 CG 图，则返回一个空数组。

你应该用全小写的**英文**词语或句子来组织提示词，并用逗号","分隔它们。只输出正向提示词，不要输出反向提示词。
一般来说，CG 图应该包含完整的场景和人物，具有高度戏剧性和细节丰富的画面。

下面是一些提示词示例，供你参考：

1boy, 1girl, cafe, couple, sitting, coffee, romantic scene, warm lighting, detailed scene, emotional moment, best quality, masterpiece, highres

1girl, looking at viewer, reaching out, forest, blue sky, river, flower, grass, bush, plant, emotional, dramatic lighting, character portrait, best quality, masterpiece, highres

示例输出：
[
  {
    "image_name": "e old_photo",
    "prompt": "(略)"
  },
  {
    "image_name": "e violet_petals",
    "prompt": "(略)"
  }
]
"""

SELECT_BEST_CG_PROMPT = """
以下的 Stable Diffusion 提示词生成了若干张图片：
{sd_prompts}

现在，请你从这些图片中挑选出最适合作为视觉小说全屏幕 CG 的一张。
要求：画面构图完整、场景和人物细节丰富、情感表达丰富、整体视觉质量好。
输出JSON格式数据，在其中指出最合适图片的序号。不要对结果进行任何解释。例如：

{{
    "best": 2
}}
"""

GENERATE_MUSIC_PROMPT = """
你是一位专业的 Stable Audio 提示词撰写员。下面，请你分析提供的Ren'Py脚本，并撰写用于生成背景音乐的提示词。
根据提供给你的Ren'Py脚本中出现的 `play music` 指令，撰写所有需要的音乐提示词。
输出JSON格式的提示词列表。JSON应当包含一个数组，数组中的每个元素包含以下几个部分：
- audio_name: 音乐的名称。需要严格遵守脚本中的名称，不要混用下划线和空格。脚本中使用下划线时，生成的图片名称也应使用下划线。空格亦然。
- prompt: 提示词列表，用于生成音乐。

应当从多个维度描述提示词，每个维度中间用竖线分隔。以下是所有可选的维度及对应的示例：

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

示例输出：
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

如果脚本中没有使用任何音乐，则返回一个空数组。
"""

GENERATE_SFX_PROMPT = """
你是一位专业的 Stable Audio 提示词撰写员。下面，请你分析提供的Ren'Py脚本，并撰写用于生成音效的提示词。
根据提供给你的Ren'Py脚本中出现的 `play sound` 指令，撰写所有需要的音效提示词。
输出JSON格式的提示词列表。JSON应当包含一个数组，数组中的每个元素包含以下几个部分：
- audio_name: 音效的名称。需要严格遵守脚本中的名称，不要混用下划线和空格。脚本中使用下划线时，生成的图片名称也应使用下划线。空格亦然。
- prompt: 提示词列表，用于生成音效。

你应该用全小写的**英文**词语或句子来组织提示词，并用逗号","分隔它们。提示词应该描述声音的特征、来源、强度等。
注意根据脚本内容反映的情境特点撰写提示词。

下面是一些提示词示例，供你参考：

door creaking open, wooden, slow, spooky, haunted house

glass breaking, shattering, crash, debris falling, impact

footsteps on wooden floor, walking, indoor, medium pace, single person

示例输出：
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

如果脚本中没有使用任何音效，则返回一个空数组。
"""

EVALUATE_IMAGE_PROMPT = """
请评估以下图像是否符合要求：
1. 图像类型：{mode}（可能是"sprite"角色立绘、"background"背景图片或"cg"场景图）
2. 使用的生成提示词：{sd_prompts}
3. 参考脚本内容：
{script_content}
4. 参考大纲信息：
{outline_content}
5. 要求：
   - 对于角色立绘(sprite)：无肢体缺失、背景干净、符合角色设定、整体视觉质量好、符合脚本中对该角色的描述
   - 对于背景图(background)：场景合理、不存在任务或不存在喧宾夺主的人物、与剧情场景一致、符合脚本中描述的环境
   - 对于CG图片(cg)：画面构图完整、场景和人物细节丰富、情感表达丰富、整体视觉质量好、与脚本中的剧情情境匹配

请思考以下问题：
1. 图像是否符合要求？(是/否)
2. 图像是否与脚本和大纲中的描述一致？(是/否)
3. 具体存在哪些问题？(如果有)
4. 如何修改当前的提示词以获得更好的结果？

请以JSON格式返回结果：
{{
    "acceptable": true/false,  // 图像是否可接受
    "issues": ["问题1", "问题2", ...],  // 存在的问题列表
    "optimized_prompt": "优化后的提示词"  // 改进的提示词
}}
"""

SCRIPT_VALIDATION_PROMPT = r"""
请解析下面的Ren'Py Lint输出，提取出所有错误及其相关信息。
输出应该是一个JSON数组，每个错误包含以下字段：
- file: 出错的文件路径
- line: 出错的行号（如果有）
- description: 错误的简短描述
- error_type: 错误类型（例如：语法错误、标签重复定义等）

Lint输出内容：
{lint_content}

只需要返回一个有效的JSON数组，不要包含任何其他解释文本。
"""

SCRIPT_FIX_PROMPT = r"""
请修复下面Ren'Py脚本中的问题。常见问题包括：
1. 素材缺失。此时应当去除脚本中对缺失素材的引用。
2. 百分号`%`引起的问题。此时应当使用`%%`来转义百分号。
3. 未定义角色。此时可以在脚本的最开头定义这个角色。
4. `with` 关键字附带的效果未定义，如 `flash`。此时应当替换为其他效果，如 `fade`。

文件: {file_name}

检测到的错误:
{error_descriptions}

当前文件内容:
```rpy
{file_content}
```

请提供修复后的完整脚本内容，仅返回修复后的脚本代码，不要添加任何说明或解释，也不要返回修复前的代码。
"""
