This module controls building output to the user. This should include logic to format output text given values. It should not contain any business logic related to decision making. 


# Adding new templates

## Step 1: Add template to `template/`
New templates should go into the `template/` directory. Placeholder text should be used be marked with `$`. 

## Step 2: Configure template in `FileManager` using `File` object
`File` object gives an easy interface for reading in files. It will keep track of the path and allow for either dynamically reading in the file or holding it in memory. This behavior can be set on the object level by using the argument `load` or if omitted, it will be based off of the setting from config, `config.LOAD_FILES`. When true, files are loaded into memory. 

`FileManager` is used to keep track of files and configure the paths. Names should be self explanatory. Class methods can be added as needed

## Step 3: Create interface to build text
Interface is designed to keep the specific file seperate from loading in the text. The specifics of how the method could be updated (ex. allow for randomness in selecting what templates to use) without effecting the chat service. 

When using a template with placeholder text, call the `substitute()` method of the `Fact` object. This should be similar to the method `Template.substitute()` where placeholder text is passed as keyword arguments.

Formating logic can be done inside these methods but should not contain any business logic. 

**YES**: logic of translating list object into list of items using proper grammer.

**NO**: logic for determining who was a top performer.
