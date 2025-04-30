import os

def convert_txt_to_html_and_edit(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        # Check if the file ends with '_message.txt'
        if file_name.endswith('_message.txt'):
            txt_file_path = os.path.join(folder_path, file_name)
            
            # Read the content of the text file
            with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
                content = txt_file.read()
            
            # Create the corresponding .html file
            html_file_name = file_name.replace('_message.txt', '_message.html')
            html_file_path = os.path.join(folder_path, html_file_name)
            
            with open(html_file_path, 'w', encoding='utf-8') as html_file:
                html_file.write(content)
            
            print(f"Converted '{file_name}' to '{html_file_name}'.")

            # Edit the original .txt file
            with open(txt_file_path, 'a', encoding='utf-8') as txt_file:
                txt_file.write("\n\n[Processed: HTML file created]")
            
            print(f"Updated '{file_name}' to indicate it has been processed.")

# Example usage
folder_path = r"E:\Tokens United\Clients\Area 13\Project Files\27-2-2025 Initial Base\website\templates\third_party\allauth\account\email"  # Replace with your folder path
convert_txt_to_html_and_edit(folder_path)