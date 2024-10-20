import anthropic
import logging
from .config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def get_image_prompts_captions(message, num_memories=4):
    prompt = f"""We're working on an art installation about memory.
    The user experience is this: the user submits a memory. We generate
    {num_memories} image-caption pair(s) for the memory, showing variations
    on the memory - the memory from different perspectives, or different
    ways the memory could have gone.

    To create each image, we will generate a prompt for the image generator
    (Stable Diffusion). This should not be the same as the caption for that
    image.
    
    The prompt is for the image generator, and should serve to prompt the 
    creation of varied, evocative images in a recognizably consistent style. 
    The user will not see the prompt.

    The caption is for the user, and should be rich in narrative, emotion, 
    and implication, hinting heavily at a larger world beyond the single
    image created by the generator.

    Here's one example:

    ```
    Prompt: Painting with detailed, palette knife-like brushstrokes of a 
    man and a woman facing each other, seated on the window ledge of a 
    small Hong Kong apartment at night. Cigarettes glow between them, 
    providing the blue night with a warm yellow glow. 
        
    Caption: Detailed painting of a man and woman in conversation on the 
    window ledge of a small, artsy bedroom. The sound of glass shattering 
    against their locked door suggests that the scheme to make her cheating 
    ex-boyfriend jealous worked a little too well, and now they're trying 
    to keep calm while waiting for the lights to go out in the living room 
    before they can dare to fall asleep.
    ```

    Please generate {num_memories} image prompt-caption pair(s) from this 
    user-submitted message:

    ```
    {message}
    ```

    The user was asked to submit a memory as their message. They may or 
    may not have done so, since we cannot control user input. Do your best
    to follow the instructions below.

    1 image prompt-caption pair should be as close to the original user
    submission as possible, while the other {num_memories - 1} should 
    contain notable deviations without losing the original completely. 

    For each image prompt:

    - Start with "Painting with detailed, palette knife-like brushstrokes" 
    for stylistic consistency.

    - Make sure every prompt includes at least one person, but you can 
    include a couple more. Avoid crowds. Portray a diverse set of subjects. 
    To do this, specifically ask for subjects of different races - white, 
    black, asian, hispanic, picking randomly with each prompt.

    - Aim to invoke a strong emotion (elation, warmth, nostalgia, melancholy) 
    with your imagery, but avoid negative emotions.

    - Include a different 'camera angle' ie. wide shot, close up, top down,
    over the shoulder, etc.

    - Include different lighting instructions ie. red, orange, yellow, blue,
    green, purple, white, etc.

    For each caption, please write in a style similar to these examples,
    but do not repeat any phrasing.

    1. A man and a woman look through elevator doors into a dark, red-lit 
    Shanghai club. They've followed each other across three countries to 
    get here, but now it's 8AM, they just stumbled to the building from a 
    taxi across a street full of people heading to work in unflinching 
    daylight, and the molly is starting to wear off but she can't get her 
    jaw to unclench.

    2. Cinematic shot of two strangers on a rooftop bar. In the background, 
    fireworks erupt from the Taipei 101, bathing the scene in purple light. 
    She tells him that she broke up with her boyfriend today, she doesn't 
    know where he is, he doesn't care about her. He'll learn later tonight, 
    miles away and hours too late, that while her story may or may not be 
    factual, it definitely isn't true.

    3. Blue-lit scene of three friends on the dance floor in a dark club. 
    Without warning, the music is silenced and a harsh spotlight shines from 
    the balcony above. An hour ago, one of them took a pill in the parking 
    lot for the first time, and now he's fighting to keep the black spots 
    from his eyes as he prepares identification for the police in a country 
    where drug use carries the death penalty.

    4. Detailed painting of a man and woman in conversation on the window 
    ledge of a small, artsy bedroom. The sound of glass shattering against 
    their locked door suggests that the scheme to make her cheating 
    ex-boyfriend jealous worked a little too well, and now they're trying 
    to keep calm while waiting for the lights to go out in the living room 
    before they can dare to fall asleep.

    Additionally:

    - Start the caption with descriptive language, before taking a more 
    narrative direction (see the examples, where the first sentence could
    be a prompt, and then the following lines diverge).

    - Aim to portray a strong emotion (elation, warmth, nostalgia) with 
    your caption, but avoid negative emotions.

    - Avoid mentioning race in the caption.

    - Avoid making up specific locations in the caption, unless the user 
    specifies a location in their submission.

    - Avoid mentioning color in the caption, unless the user specifies a
    color in their submission.

    - The caption should be between 65-75 words.

    Send each image prompt-caption pair as a python-formatted dictionary in 
    a list. Example:
    ```
    [
        {{
            "prompt": "Prompt 1",
            "caption": "Caption 1",
        }},
        {{
            "prompt": "Prompt 2",
            "caption": "Caption 2",
        }},
        {{
            "prompt": "Prompt 3",
            "caption": "Caption 3",
        }},
        {{
            "prompt": "Prompt 4",
            "caption": "Caption 4",
        }},
    ]
    ```

    DO NOT INCLUDE ANYTHING IN YOUR RESPONSE OTHER THAN THE LIST. Your response 
    will be consumed by a pipeline, and deviating from the list format will 
    break the pipeline.
    """

    try:
        logging.debug(f"Prompting Claude")
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        logging.debug(f"Received response: {response}")

        return response.content[0].text.strip('"')

    except Exception as e:
        logging.error(f"Error getting Claude response: {e}")
        return "Unable to get response at this time."
