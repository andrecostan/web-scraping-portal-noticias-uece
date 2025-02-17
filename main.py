import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver(headless=True):
    """Configura e retorna uma instância do WebDriver no modo headless."""
    options = webdriver.ChromeOptions()
    
    if headless:
        options.add_argument("--headless=new")           # Usa o modo headless atualizado
        options.add_argument("--disable-gpu")            # Necessário em alguns sistemas para evitar erros gráficos
        options.add_argument("--no-sandbox")             # Recomendado para execução em ambientes Linux
        options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória compartilhada
    
    return webdriver.Chrome(options=options)

def post_count(driver):
    """Conta quantos posts existem na página dentro da div cc-posts."""
    try:
        posts_div = driver.find_element(By.CLASS_NAME, "cc-posts")
        return len(posts_div.find_elements(By.CLASS_NAME, "cc-post"))
    except Exception as e:
        print(f"Erro ao contar posts: {e}")
        return 0

def extract_posts(driver):
    """Extrai os títulos e descrições dos posts."""
    print("Extraindo posts")
    try:
        posts_div = driver.find_element(By.CLASS_NAME, "cc-posts")
        soup = BeautifulSoup(posts_div.get_attribute('innerHTML'), 'html.parser')

        titles = [title.text.strip() for title in soup.find_all("h3")]
        descriptions = [desc.text.strip() for desc in soup.find_all(class_="cc-post-excerpt")]
        
        if len(titles) != len(descriptions):
            raise ValueError("Número de títulos e descrições não corresponde.")
        
        return dict(zip(titles, descriptions))
    except Exception as e:
        print(f"Erro ao extrair posts: {e}")
        return {}

def save_posts_to_json(posts, filename="results.json"):
    """Salva os posts extraídos em um arquivo JSON."""
    print("Salvando posts")
    try:
        df = pd.DataFrame(list(posts.items()), columns=["Title", "Description"])
        df.to_json(filename, orient="records", force_ascii=False, indent=4)
        print("Web Scraping finalizado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar posts: {e}")

def load_posts(driver, wait, max_posts):
    """Carrega mais posts clicando no botão de carregamento até atingir o limite."""
    print("Carregando posts")
    button_selector = ".cc-button"
    try:
        button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, button_selector)))
        
        while post_count(driver) <= max_posts:
            driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector)))
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
            #print(f"Total de posts carregados: {post_count(driver)}")
    except Exception as e:
        print(f"Erro ao carregar mais posts: {e}")

def main():
    """Executa o processo de scraping."""
    driver = setup_driver(headless=True)
    wait = WebDriverWait(driver, 10)
    url = "https://www.uece.br/uece/noticias/"
    
    try:
        driver.get(url)
        load_posts(driver, wait, 50)
        posts = extract_posts(driver)
        save_posts_to_json(posts)
    finally:
        # input("Pressione ENTER para fechar o navegador...")
        driver.quit()

if __name__ == "__main__":
    main()
