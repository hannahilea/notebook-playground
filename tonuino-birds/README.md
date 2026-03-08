# `tonuino-birds`

In service of setting up TonUINO cards with bird songs.   

## Punch list

- [x] Make a list
- [x] Try adding single card for single song
    - [x] Program on-board tonuino
- [x] Try bulk add via https://github.com/mxmehl/tonuino-cards-manager
    - [x] Follow install
    - [x] Set up yaml manually
    - [x] Use yaml to program one card
    - [ ] ...does it work? TBD! 
- [ ] From card deck, list out all required birds
- [ ] Auto-generate bulk .yaml from bird list
    - [ ] Add audio files for each bird
    - [ ] Run to put audio files onto tonuino
    - [ ] Test with one manual card that bulk-add worked
- [ ] Set up cards!
    - [ ] Program stickers
    - [ ] Put sticker on card


## Dev log

### Goal one: set up card manager

Want to use: https://github.com/mxmehl/tonuino-cards-manager

1. Installation:
    Did (from this working directory):
    ```
    uv init --bare

    uv add tonuino-cards-manager
    ```

    Then to run it, still from this working directory, do 
    ```
    uv run tonuino-cards-manager --help
    ```
    ! 
    Okay, it works! Great. 

2. Try a test config, save it locally

    ```
    mkdir output_test_dir

    uv run tonuino-cards-manager --config test1.yaml --destination output_test_dir
    ```

    What did that do? Interesting: printed a QR code to stdout! 
    ```
    tonuino-birds$ tree output_test_dir
    output_test_dir
    └── 01
        ├── 001-George_B_ReynardMacaulay_Library-American_Crow_09_Calls_US-FL.mp3
        └── 002-Jay_McGowanMacaulay_Library-Blue-headed_Vireo_10_Calls_US-NY.mp3
    ```
    Okay, nice! So the names are preserved, which is awesome. There's also a TOC_test.pdf saved at the top level. (Looks like there's a flag to turn it off, but it seems useful)

    -  Try it a second time after updating the card number in the test1.yaml to "3". ...ooh, gave me a "non-consecutive" warning. can i force it? nope, doesn't seem like it.

    - Okay, and if I rerun the original file a second time, it overwrites without complaint, even without the -f flag. Iiiiiinteresting. 

    - Now add some cruft in the folder. Do those get erased?
        ```
        mkdir output_test_dir/advert
        touch output_test_dir/advert/foo.mp3
        ```
    Then rerun. Nope, those files are still there! Great.

    - What if we run forced? e.g.
    ```
    uv run tonuino-cards-manager --config test1.yaml --destination output_test_dir -f
    ```
    Nope, no deletion! Ah, from help docs, `-f` only deletes AUDIO files on the destination that are not managed by user. Great!

    - Also, there's a nice `-v` verbose option with this tool!

3. Okay, the one problem I foresee is that the generated QR codes are ephemeral (in the terminal). Can I get those into a file?

    ```
    uv run tonuino-cards-manager --config test1.yaml --destination output_test_dir > test1.log
    ```
    Okay, great. My IDE shows the formatting a little strangely, but I can dump it back into my terminal to see the nicely formatted QR codes once more:
    ```
    cat test1.log

    # Or for paging through long files...
    less test1.log
    ```

    Okay! I am impressed with how well this tool works out of the box. Very nice!

4. Let's attempt to write the files to my SD card instead of a local file.

    When setting up my SD card I named it `TONUINO`; that's what shows up when SD card is inserted

    ```
    uv run tonuino-cards-manager --config test1.yaml --destination '/Volumes/TONUINO' > test1.log
    ```

    Running `tree /Volumes/TONUINO` shows that those new files are on there!!

    Let's make a test2.yaml so that we can compare behavior of two separate cards.

    Seems fine locally; let's put it on the card!

    ```
    uv run tonuino-cards-manager --config test2.yaml --destination '/Volumes/TONUINO' > test2.log
    ```

### Goal two: set up the cards

Okay. SD card is in device. Device is powered on. Now what?!

- According to the set-up instructions for the manager, https://marc136.github.io/tonuino-nfc-tools/ . Let's give that a go.
    - ...nope. Android only, and I don't have access to an Android device. (Maybe AF has an old one I can use?)

- Trying NFC Tools on iphone
    - Okay, this seems v. powerful. only question is how to get the info from the QR code to this app! lol. 
    - Do NOT bother upgrading to PRO. 

- Trying different tools app---claims to support bulk CSV (with paid) --- 3day trial, let's see how it goes
    - Played around, no success yet---also, VERY manual.

- [ ] TODO Next: figure out csv bulk upload situation (may take...a bit. does not seem intuitive)

### Goal 3: List the cards from the birds deck
- Doing that in birds-of-north-america-deck.txt
