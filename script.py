import re
import os
import sys
def parse_subject_responses(input_text):
    output = []
    current_subject = ""
    
    for line in input_text.split('\n'):
        if line.startswith("Subject"):
            if current_subject:
                output.append("")  # Add a blank line between subjects
            current_subject = line.strip()
            output.append(current_subject)
        elif re.match(r'^\d+\.', line):
            parts = line.split('\t')
            if len(parts) >= 3:
                question_number = parts[0].split('.')[0].strip()
                response = parts[2].strip()
                output.append(f"{question_number}\t{response}")

    return "\n".join(output)

def modify_files():
    for filename in [os.path.join(sys.path[0], "answerkey.txt"), os.path.join(sys.path[0], "responses.txt")]:
        with open(filename, 'r') as file:
            input_text = file.read()
        output_text = parse_subject_responses(input_text)
        with open(filename, 'w') as file:
            file.write(output_text)

def read_file(filename):
    subjects = {}
    current_subject = ""
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Subject"):
                current_subject = line.split(":")[1].split("(")[0].strip()
                subjects[current_subject] = []
            elif line and line[0].isdigit():
                parts = line.split()
                if len(parts) >= 2:
                    subjects[current_subject].append(parts[-1])
    return subjects

def compare_answers(response, answer_key):
    results = {}
    for subject in response:
        if subject not in answer_key:
            print(f"Warning: Subject '{subject}' not found in answer key.")
            continue
        correct = 0
        incorrect = 0
        skipped = 0
        wrong_answers = []
        for i, (resp, key) in enumerate(zip(response[subject], answer_key[subject]), 1):
            if resp == '-':
                skipped += 1
            elif resp == key:
                correct += 1
            else:
                incorrect += 1
                wrong_answers.append((i, resp, key))
        
        score = (correct * 5) + (incorrect * -1)
        total_marks = 250 if "General Test" in subject else 200
        
        results[subject] = {
            'correct': correct,
            'incorrect': incorrect,
            'skipped': skipped,
            'score': score,
            'total_marks': total_marks,
            'wrong_answers': wrong_answers
        }
    return results

def write_results_to_file(results, grand_total_score, grand_total_marks):
    with open('result.txt', 'w') as file:
        for subject, scores in results.items():
            file.write(f"\nSubject: {subject}\n")
            file.write(f"Correct: {scores['correct']}\n")
            file.write(f"Incorrect: {scores['incorrect']}\n")
            file.write(f"Skipped: {scores['skipped']}\n")
            file.write(f"Score: {scores['score']} out of {scores['total_marks']}\n")
            
            if scores['wrong_answers']:
                file.write("Wrong Answers:\n")
                for question, given_answer, correct_answer in scores['wrong_answers']:
                    file.write(f"  Question {question}: Given {given_answer}, Correct {correct_answer}\n")

        file.write("\n" + "="*30 + "\n")
        file.write("GRAND TOTAL\n")
        file.write("="*30 + "\n")
        file.write(f"Total Score: {grand_total_score} out of {grand_total_marks}\n")

def main():
    try:
        # Step 1: Modify the text files
        modify_files()

        # Step 2: Process and calculate results
        response = read_file(os.path.join(sys.path[0], "responses.txt"))
        answer_key = read_file(os.path.join(sys.path[0], "answerkey.txt"))
        results = compare_answers(response, answer_key)

        grand_total_score = 0
        grand_total_marks = 0

        for subject, scores in results.items():
            print(f"\nSubject: {subject}")
            print(f"Correct: {scores['correct']}")
            print(f"Incorrect: {scores['incorrect']}")
            print(f"Skipped: {scores['skipped']}")
            print(f"Score: {scores['score']} out of {scores['total_marks']}")
            
            if scores['wrong_answers']:
                print("Wrong Answers:")
                for question, given_answer, correct_answer in scores['wrong_answers']:
                    print(f"  Question {question}: Given {given_answer}, Correct {correct_answer}")

            grand_total_score += scores['score']
            grand_total_marks += scores['total_marks']

        # Print grand total
        print("\n" + "="*30)
        print("GRAND TOTAL")
        print("="*30)
        print(f"Total Score: {grand_total_score} out of {grand_total_marks}")

        # Step 3: Write results to result.txt
        write_results_to_file(results, grand_total_score, grand_total_marks)

        print("\nResults have been written to result.txt")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()