# `tonuino-birds`

In service of setting up TonUINO cards with bird songs.

Project write-up here:  [Birduino: A card-triggered audio player for [learning] the birds](https://hannahilea.com/blog/birduino)

## Punch list

- [x] Make a list
- [x] Try adding single card for single song
    - [x] Program on-board tonuino
- [x] Try bulk add via https://github.com/mxmehl/tonuino-cards-manager
    - [x] Follow install
    - [x] Set up yaml manually
    - [x] Use yaml to program one card
    - [x] ...does it work? TBD!
- [x] From card deck, list out all required birds
- [x] Auto-generate bulk .yaml from bird list
    - [x] Add audio files for each bird
    - [x] Run to put audio files onto tonuino
    - [x] Test with one manual card that bulk-add worked
- [x] Set up cards!
    - [x] Put stickers on card
    - [x] Program stickers

## Dev log

### Goal 1: set up card manager

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

### Goal 2: Prepare to make full .yaml

1. List the cards from the birds deck
- ...added as `birds-of-north-america-deck.txt`

2. Make list of audio files (so that we don't have to constantly parse)
```
ls "/Users/skye/Downloads/The Cornell Guide to Bird Sounds--United States and Canada (v2025)" | wc
    4961   26272  190133
```
Okay, 4961 lines == 4961 files. pretty sure that's what we were promised?

```
ls "/Users/skye/Downloads/The Cornell Guide to Bird Sounds--United States and Canada (v2025)" > audio-full-tracklist.txt
```

### Goal 3: Make full playlist of birds!

Okay. This is a case where templating the full thing would be overkill. There are two steps:

1. Automated: loop through deck, find matching audio tracks

2. Manual: Add header info to .yaml file, remove junk files, manually do tuning

Let's do the automated bit first! Written in script `make_bird_yaml.sh`, so can be run as
```
bash make_bird_yaml.sh
```
WILL overwrite existing `tonuino-birds-of-north-america.yaml` file.

:) :) :)

It's looking good! Okay. Let's check that in (so we don't accidentally overwrite it!) and then do the manual bit.

#### ...manually clean up playlist

Okay. Skimming through by eye looking for the birds with no matches. Could automate this, but not worth it (I'm learning!). What do we have?

- Gadwell
- Yellow-crowned Night-Heron

...that's it. wow! Okay. And it turns out the Gadwell issue is because I misspelled it, and it's actually "Gadwall". Hah! manually copied those files over.

Similarly, in the audio it is stylized as "Yellow-crowned Night Heron". Copied over!


### Goal 4: set up the cards

Okay. SD card is in device. Device is powered on. Now what?!

- According to the set-up instructions for the manager, https://marc136.github.io/tonuino-nfc-tools/ . Let's give that a go.
    - ...nope. Android only, and I don't have access to an Android device. (Maybe AF has an old one I can use?)

- Trying NFC Tools on iphone
    - Okay, this seems v. powerful. only question is how to get the info from the QR code to this app! lol.
    - Do NOT bother upgrading to PRO.

- Trying different tools app---claims to support bulk CSV (with paid) --- 3day trial, let's see how it goes
    - Played around, no success yet---also, VERY manual.

- Next: figure out csv bulk upload situation (may take...a bit. does not seem intuitive)

- Can we get even a single card programmed from my phone?
- We got one programmed by the phone?

- Programmed one with the tonuino. debug info says:
```
NTAG215
21:49:42.178 -> Writing: 13 37 b3 47 02 01 09 01 05
```

- Can we read that from our phone app? What does it look like there?
    - Scanned with NFC tools
    - Type: Tex record: T (0x54)
    - Payload: 13 bytes
        0x02 0x65 0x6E 0x32 0x30 0x31 0x30 0x33 0x30 0x30 0x13 0x37 0xB3

- Okay. How does that line up with what we claimed to be writing??

- Thank you, https://www.scadacore.com/tools/programming-calculators/online-hex-converter/

...it is hairy to figure out how to configure a text-as-bytes record in this app. surely there's a way, but I cannot figure it out.

- okay instead, tried the QR import again. This time...it worked!!

- Okay. I actively dislike NFC.cool and it feels bad SO uninstalling and cancelling the free trial.
- We're just going to manually import-single-QR-code-and-save-it with NFC Tools. Fine! At least we know that works.

First though: It seems very much like "party" mode has some bugs (in general, or maybe just on my somewhat older mp3 module?)
    - https://discourse.voss.earth/t/tonuino-3-1-party-modus-error/12689

Let's bypass this by using a different mode in our yaml. Luckily as long as the order of the yaml stays the same, we can regenerate our QR codes as much as we want!

- Okay fixed up the random mode. We good! Regenerate our QR codes.

```
uv run tonuino-cards-manager --config tonuino-birds-of-north-america.yaml --destination 'temp' &> tonuino-birds-of-north-america.log
```

- Huh. There is a mismatch between what the card claims to be reading in when device-configured
        ` `
    and what it reads in when bulk-configured:
        `13 37 B3 47 02 01 09 01 0e` (spaces added)
    which SHOULD mean "folder 1 party-to-from mode track 1 to track 14`

    So the question is now "where is that 7th byte coming from in the QR code generator?!"
    Because either there's a bug there OR (more likely) my yaml is weird in some way....

- When QR generation is run with verbose flag, it returns `13 37 B3 47 02 01 09 01 0e`
    so at least we know that the code is being read correctly. What does it mean??

- Let's read the code!
    - https://github.com/mxmehl/tonuino-cards-manager/blob/b8d607327799524be14f728509bd70f6b9ca87a8/tonuino_cards_manager/main.py#L81

    - AH "13 37 B3 47" is the cookie! Set in yaml, same as set on tonuino, same everywhere. okay.
    - Remaining 5 bytes: 3 differs. Looks like third is "mode". huh.

...BAIL. this is fruitless.

- Found AF's old android phone; couldn't install https://marc136.github.io/tonuino-nfc-tools/ via app store ("invalid country") but succeeded via F-droid.
    - Using this app was seamless. AMAZING.

### Goal 5: Do the thing!

No, but seriously! The final steps are:
- [x] Run the real command to copy the audio over to the SD card:
```
    uv run tonuino-cards-manager --config tonuino-birds-of-north-america.yaml --destination '/Volumes/TONUINO' &> tonuino-birds-of-north-america.log
```

- [x] Program each sticker...
    - [x] ...and put it on the bird card

...and that's it, on this side of the project. Still need to figure out a physical housing, but that's neither here nor there.

:)

Huzzah!

(But seriously, this worked out way better than I expected it to.)
