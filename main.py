import string
import re
import random
from collections import Counter

def read_corpus(file) -> list:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    tokens = content.lower().split()
    clean = []
    for word in tokens:
        token = re.sub(r"[^a-záéíóúüñ]", "", word)
        if token:
            clean.append(token)
    return clean

#we need to count every time a bigram appears
def build_bigram(text:list) -> dict:
    bigram = {}
    #iterate len - 1 of text so we can keep track of the last pair without going out of bounds
    for i in range (len(text) - 1):
        pair = (text[i], text[i + 1])
        #if pair is in bigram + 1
        if pair in bigram:
            bigram[pair] += 1
        #else add bigram
        else:
            bigram[pair] = 1
    return bigram

def check_freq(bigram_list:dict, threshold:int) -> dict | str:
    filtered = {pair:freq for pair, freq in bigram_list.items() if freq >= threshold}
    if filtered:
        return filtered
    return "Theres no bigrams with this frequency"

#function to check the frequency of a pair of words
def check_word(desired_word:str, text:list) -> int | str:
    counter = 0 
    for word in text:
        if desired_word == word:
            counter += 1
    return counter

#check desired word frequency
def create_vocabulary(text) -> set:
    #set doesn't allow duplicates so its easiers
    words = set()
    for word in text:
        token = re.sub("[^a-záéíóúüñ]", "", word)
        if token:
            words.add(token)
    return words

#create unique words with index
def create_unique_words(text) -> dict:
    dictionary = {word:index for index,word in enumerate(text)}
    return dictionary

#dios: 15651
#dijo: 23534,
#create sequence of words with two known and logic words and then append another 23
def create_persona(seed:list, vocab_size:int) -> list:
    individual = seed[:]
    for i in range(25-len(seed)):
        individual.append(random.randint(0, vocab_size - 1))
    return individual

#we get the indexes of each of the personas we created above
def decode(individual:list, vocabulary:dict) -> list:
    invert_dict = {idx:word for word, idx in vocabulary.items()}
    word_list = []
    for index in individual:
        word_list.append(invert_dict[index])
    return word_list

#get score
#if one of the pair of words in our decoded word appears in the list of bigrams we augment the score
def fitness(individual: list, vocabulary: dict, bigram:dict) -> int:
    words = decode(individual, vocabulary)
    score = 0
    for i in range(len(words) - 1):
        pair = (words[i], words[i + 1])
        score +=bigram.get(pair, 0)
    return score

def penalization_repeticiones(words: list) -> int:
    if not words:
        return 0

    penalization = 0

    # repeticiones contiguas
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            penalization += 30

    total = len(words)
    count = Counter(words)
    limit = total * 0.08  # antes 0.20, ahora máximo 2 veces por word (8% de 25 = 2)

    for palabra, frequency in count.items():
        if frequency > limit:
            exceso = frequency - limit
            penalization += int(exceso * 500) # 500 de penalizacion

    return penalization

def fitness_with_penalization(individual: list, vocabulary: dict, bigrams: dict) -> int:
    words = decode(individual, vocabulary)
    score = fitness(individual, vocabulary, bigrams)
    penalization = penalization_repeticiones(words)
    return score - penalization

def create_population(size: int, seed: list, vocab_size: int) -> list:
    population = []
    for i in range(size):
        population.append(create_persona(seed, vocab_size))
    return population

def tournament_selection(population: list, vocabulary: dict, bigrams: dict) -> list:
    contenders = random.sample(population, 3)
    winner = max(contenders, key=lambda ind: fitness_with_penalization(ind, vocabulary, bigrams))
    return winner

def crossover(parent1: list, parent2: list, n_seed: int) -> tuple:
    point = random.randint(n_seed + 1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(individual: list, vocab_size: int, n_seed: int, rate: float) -> list:
    mutant = individual[:]
    for i in range(n_seed, len(mutant)):
        if random.random() < rate:
            mutant[i] = random.randint(0, vocab_size - 1)
    return mutant

def run_ga(generations: int, pop_size: int, seed: list,
           vocab_size: int, vocabulary: dict, bigrams: dict) -> list:

    population = create_population(pop_size, seed, vocab_size)
    best_individual = None
    best_fitness = float('-inf')

    for gen in range(generations):
        # calcular fitness de todos
        fitnesses = [fitness_with_penalization(ind, vocabulary, bigrams) for ind in population]

        sorted_pop = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        new_population = [population[i][:] for i in sorted_pop[:5]]

        # trackear el mejor
        best_idx = sorted_pop[0]
        if fitnesses[best_idx] > best_fitness:
            best_fitness = fitnesses[best_idx]
            best_individual = population[best_idx][:] 

        while len(new_population) < pop_size:
            p1 = tournament_selection(population, vocabulary, bigrams)
            p2 = tournament_selection(population, vocabulary, bigrams)
            c1, c2 = crossover(p1, p2, len(seed))

            # mutación adaptativa — sube si llevamos muchas gens sin mejorar
            gens_sin_mejora = gen - last_improvement if 'last_improvement' in dir() else 0
            tasa = 0.15 + (0.30 if gens_sin_mejora > 15 else 0)

            c1 = mutate(c1, vocab_size, len(seed), tasa)
            c2 = mutate(c2, vocab_size, len(seed), tasa)
            new_population.append(c1)
            new_population.append(c2)

        population = new_population[:pop_size]

        if fitnesses[best_idx] > best_fitness:
            last_improvement = gen

        best_words = decode(best_individual, vocabulary)
        pen = penalization_repeticiones(best_words)

        print(f"Gen {gen+1:03d} | Pen: {pen:4d} | Fit: {best_fitness:6d} | {' '.join(best_words)}")

    return best_individual

if __name__ == "__main__":
    list_of_words = read_corpus("biblia.txt")
    bigram_count = build_bigram(list_of_words)

    # --- CAMBIO 1: vocabulario reducido a las 500 words más frecuentes ---
    word_freq = Counter(list_of_words)
    top_words = [word for word, _ in word_freq.most_common(500)]
    unique_words = {word: idx for idx, word in enumerate(top_words)}
    vocab_size = len(unique_words)
    # -------------------------------------------------------------------------


    seed = [unique_words["dios"], unique_words["dijo"]]

    # --- CAMBIO 2: población de 300 en lugar de 100 ---
    best = run_ga(
        generations=200,
        pop_size=300,       # <-- 100 a 300
        seed=seed,
        vocab_size=vocab_size,
        vocabulary=unique_words,
        bigrams=bigram_count
    )
