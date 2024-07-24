# General Information
This is a small project that automates searching for MARC records, freeing up time for library staff to continue doing their work. Please be aware that the scripts will:

1. Create, modify, and delete files on your computer. It will only modify user-specified files and only delete files it created.
2. Open a browser on your computer and navigate through the Library of Congress website for books.

## Prerequisites
This program uses Chrome. Please make sure you have the newest version of Chrome installed on your computer.

### Installing Dependencies For the First Time
Python is not enough for this program to run. You will need to install some packages.
1. Open command prompt
2. Enter `cd Documents/GitHub/MARC-recordfinder`
3. Enter `pip install -r requirements.txt`.

**You only need to do this the first time you run this program.** Afterwards, just remember to update your dependencies (see below).

## Before You Run

### Update Your Dependencies
1. Open command prompt
2. Enter `cd Documents/GitHub/MARC-recordfinder`
2. Enter `pip install -r requirements.txt --upgrade` and allow to finish

### Required Headers
The scripts expect to receive a specifically formatted file. Your titles should be organized in a CSV file with the following headers, **spelled exactly**:
- LCCN
- ISBN
- Short Title
- Author
- Copyright Year

### Optional Headers
- Notes
  - Write "skip" in the Notes section to skip certain titles from being searched.
- Call No.

It is not necessary for each book to have every single value, but each entry will need **either** LCCN, ISBN, or [Short Title, Author, and Copyright Year].

## Running the Program
1. Make sure your CSV is named `MM.DD_restOfFilename.csv`.
2. Move your CSV file into the `../MARC-recordfinder`.
4. If your LCCN are not formatted with zeroes, first run `zeroAdder.py`
5. Then run `MARCRecordFinder.py`

At the end of the session, you will have a `collection_records.mrc` file that you can then use to import records into the digital catalog. In addition, the script may also product a `not_found.csv`, `skipped.csv`, or `multilink.csv`, depending on the results of its search. These contain titles that may need manual inspection.

Before you run another batch, make sure to move all result files out of `/MARC-recordfinder`.

If you run into any problems, please screenshot the error message if you can and then email me at **melissa@slgardens.org**.