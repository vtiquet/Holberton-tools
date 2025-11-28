from bs4 import BeautifulSoup
import urllib.parse  # Pour décoder les URL

def generer_readme(fichier_html):
    """
    Génère un README.md avec gestion des retours à la ligne dans le code
    et correction des liens de ressources.
    """
    try:
        with open(fichier_html, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Erreur: Le fichier '{fichier_html}' n'a pas été trouvé.")
        return
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier HTML: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    readme_content = []

    # --- 1. Bannière  ---
    readme_content.append('<div align="center"><img src="https://github.com/vtiquet/holbertonschool-resources/blob/main/image/Holberton-Logo.svg" width=40% height=40%/></div>\n\n')

    # --- 2. Titre du Projet  ---
    project_description = soup.find(id="project-description")
    titre_projet = project_description.find('h2').text.strip() if project_description and project_description.find('h2') else "Titre du Projet (à remplacer)"
    readme_content.append(f"# {titre_projet}\n\n")

    # --- 3. Sommaire  ---
    readme_content.append("## Table of Contents :\n\n")
    tasks = soup.find_all('div', class_='panel panel-default task-card')
    if tasks:
        tasks.pop()
    for i, task in enumerate(tasks):
        task_title_tag = task.find('h3', class_='panel-title')
        task_title = task_title_tag.get_text(strip=True) if task_title_tag else f"Titre de la tâche {i+1} (à remplacer)"
        task_title = task_title.lstrip('0123456789. ') 
        readme_content.append(f"  - [{i}. {task_title}](#subparagraph{i})\n")

    # --- 4. Resources  ---
    resources_section = soup.find('h2', string='Resources')
    if resources_section:
        readme_content.append("\n## Resources\n")
        resource_list = resources_section.find_next('ul')
        if resource_list:
            readme_content.append("### Read or watch:\n")
            for li in resource_list.find_all('li'):
                link = li.find('a')
                if link:
                    href = link.get('href', '#')
                    if href.startswith('/redirect'):
                        parsed_url = urllib.parse.urlparse(href)
                        query_params = urllib.parse.parse_qs(parsed_url.query)
                        if 'url' in query_params:
                            real_url = urllib.parse.unquote(query_params['url'][0])  
                            readme_content.append(f"* [{link.text}]({real_url})\n")
                        else:
                            readme_content.append(f"* [{link.text}]({href})\n") 
                    else:
                         readme_content.append(f"* [{link.text}]({href})\n") 



    # --- 5. Learning Objectives, 6. Requirements  ---
    learning_objectives_section = soup.find('h2', string='Learning Objectives')
    if learning_objectives_section:
        readme_content.append("\n## Learning Objectives\n")
        learning_objectives_list = learning_objectives_section.find_next('ul')
        if learning_objectives_list:
            readme_content.append("At the end of this project, you are expected to be able to explain to anyone, without the help of Google:\n")
            for li in learning_objectives_list.find_all('li'):
                readme_content.append(f"* {li.get_text(strip=True)}\n")

    requirements_section = soup.find('h2', string='Requirements')
    if requirements_section:
        readme_content.append("\n## Requirements\n")
        requirements_list = requirements_section.find_next('ul')
        if requirements_list:
            readme_content.append("### General\n")
            for li in requirements_list.find_all('li'):
                readme_content.append(f"* {li.get_text(strip=True)}\n")

    # --- 7. Consignes des Tâches ---
    readme_content.append("\n## Task\n")

    for i, task in enumerate(tasks):
        task_title_tag = task.find('h3', class_='panel-title')
        task_title = task_title_tag.get_text(strip=True) if task_title_tag else f"Titre de la tâche {i+1} (à remplacer)"
        task_title = task_title.lstrip('0123456789. ')  # Enleve le numero, point, espace
        readme_content.append(f"### {i}. {task_title} <a name='subparagraph{i}'></a>\n\n")

        task_body = task.find('div', class_='panel-body')
        if task_body:
            def process_element(element, indent_level=0):
                if element.name == 'p':
                    paragraph_text = "".join(str(content) if isinstance(content, str) else "\n" if content.name == 'br' else str(content) for content in element.contents)
                    return paragraph_text.strip() + "\n\n"

                elif element.name == 'ul':
                    list_content = ""
                    for li in element.find_all('li', recursive=False):
                        list_item_text = "".join(str(content) if isinstance(content, str) else "\n" + process_element(content, indent_level + 1) if content.name == 'ul' else str(content) for content in li.contents)
                        list_content += "  " * indent_level + f"* {list_item_text.strip()}\n"
                    return list_content + "\n"

                elif element.name == 'pre':
                    code_content = element.find('code')
                    if code_content:
                        language = ""
                        for cls in code_content.get('class', []):
                            if cls.startswith('language-'):
                                language = cls.split('-')[1]
                                break  

                        
                        code_text = code_content.get_text()
                        code_text = code_text.strip()
                        return f"```{language}\n{code_text}\n```\n\n"
                elif element.name == 'strong':
                     return f"**{element.get_text(strip=True)}**"
                elif element.name == 'em':
                    return f"*{element.get_text(strip=True)}*"

                return ""

            for element in task_body.find_all(['p', 'ul', 'pre','strong','em'], recursive=False):
                readme_content.append(process_element(element))

        readme_content.append("---\n\n")

    # --- 8. Authors ---
    readme_content.append("\n## Authors\n")
    readme_content.append("vtiquet - [GitHub Profile](https://github.com/vtiquet)\n")

    # --- Écriture du fichier README.md ---
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("".join(readme_content))

    print("README.md généré avec succès!")

generer_readme("projet.html") 