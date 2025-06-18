# scheduler_learning_searching.py
"""
Versi aman dari scheduler.py
Menggunakan AI berbasis Genetic Algorithm (GA)
Menerapkan prinsip Learning (via evolusi fitness) & Searching (via heuristik GA)
"""

import random
import pandas as pd
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Schedule:
    assignments: List[Tuple]  # (mata_kuliah_index, hari, sesi, ruangan)
    fitness: float = 0.0

class AIScheduler:
    def __init__(self, matkul_df, dosen_df, kelas_df, ruangan_df,
                 population_size=100, generations=300,
                 mutation_rate=0.1, crossover_rate=0.8, elite_size=10):
        self.matkul_df = matkul_df
        self.dosen_df = dosen_df
        self.kelas_df = kelas_df
        self.ruangan_df = ruangan_df

        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size

        self.HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
        self.SESI = [1, 2, 3, 4, 5]

        self._preprocess()

    def _parse_list(self, text):
        if pd.isna(text): return []
        try:
            return [x.strip() for x in str(text).split(',') if x.strip()]
        except:
            return []

    def _safe_int_list(self, text):
        result = []
        for x in self._parse_list(text):
            try:
                result.append(int(float(x)))
            except:
                continue
        return result

    def _preprocess(self):
        self.dosen_dict = self.dosen_df.set_index("kode_dosen").to_dict("index")
        self.kelas_dict = self.kelas_df.set_index("kode_kelas").to_dict("index")
        self.ruangan_dict = self.ruangan_df.set_index("kode_ruang").to_dict("index")

        for info in self.dosen_dict.values():
            info["preferensi_hari_list"] = self._parse_list(info.get("preferensi_hari", ""))
            info["preferensi_sesi_list"] = self._safe_int_list(info.get("preferensi_sesi", ""))

        for info in self.ruangan_dict.values():
            info["tersedia_hari_list"] = self._parse_list(info.get("tersedia_hari", ""))
            info["tersedia_sesi_list"] = self._safe_int_list(info.get("tersedia_sesi", ""))

    def _get_valid_slots(self, matkul, used):
        valid = []
        d_info = self.dosen_dict.get(matkul['dosen'], {})
        k_info = self.kelas_dict.get(matkul['kelas'], {})
        n_mhs = k_info.get('jumlah_mahasiswa', 0)
        for h in d_info.get('preferensi_hari_list', self.HARI):
            for s in d_info.get('preferensi_sesi_list', self.SESI):
                for r_id, r_info in self.ruangan_dict.items():
                    if r_info.get('kapasitas', 0) < n_mhs: continue
                    if h not in r_info.get('tersedia_hari_list', self.HARI): continue
                    if s not in r_info.get('tersedia_sesi_list', self.SESI): continue
                    if (h, s, r_id) in used or (h, s, matkul['kelas']) in used or (h, s, matkul['dosen']) in used:
                        continue
                    valid.append((h, s, r_id))
        return valid

    def generate_population(self) -> List[Schedule]:
        population = []
        for _ in range(self.population_size):
            assignments = []
            used = set()
            for idx, matkul in self.matkul_df.iterrows():
                slot = self._get_valid_slots(matkul, used)
                if slot:
                    h, s, r = random.choice(slot)
                else:
                    h, s = random.choice(self.HARI), random.choice(self.SESI)
                    r = random.choice(list(self.ruangan_dict))
                assignments.append((idx, h, s, r))
                used.update({(h, s, r), (h, s, matkul['kelas']), (h, s, matkul['dosen'])})
            sched = Schedule(assignments)
            sched.fitness = self.fitness(sched)
            population.append(sched)
        return population

    def fitness(self, sched: Schedule):
        score = 1000
        penalty, bonus = 0, 0
        used = set()
        for idx, h, s, r in sched.assignments:
            m = self.matkul_df.iloc[idx]
            d, k = m['dosen'], m['kelas']
            if (h, s, r) in used: penalty += 100
            if (h, s, d) in used: penalty += 100
            if (h, s, k) in used: penalty += 100
            used.update({(h, s, r), (h, s, d), (h, s, k)})
            d_info = self.dosen_dict.get(d, {})
            if h in d_info.get("preferensi_hari_list", []): bonus += 5
            if s in d_info.get("preferensi_sesi_list", []): bonus += 5
            if h not in self.ruangan_dict.get(r, {}).get("tersedia_hari_list", []): penalty += 10
            if s not in self.ruangan_dict.get(r, {}).get("tersedia_sesi_list", []): penalty += 10
        return max(score + bonus - penalty, 0)

    def evolve(self) -> Schedule:
        pop = self.generate_population()
        best = max(pop, key=lambda x: x.fitness)
        for gen in range(self.generations):
            selected = [max(random.sample(pop, 5), key=lambda x: x.fitness) for _ in range(len(pop))]
            children = pop[:self.elite_size]
            while len(children) < self.population_size:
                p1, p2 = random.sample(selected, 2)
                c1, c2 = self.crossover(p1, p2)
                children.extend([self.mutate(c1), self.mutate(c2)])
            pop = children[:self.population_size]
            current = max(pop, key=lambda x: x.fitness)
            if current.fitness > best.fitness:
                best = current
        return best

    def crossover(self, p1: Schedule, p2: Schedule):
        if random.random() > self.crossover_rate:
            return p1, p2
        size = len(p1.assignments)
        s, e = sorted(random.sample(range(size), 2))
        def make_child(a, b):
            child = [None]*size
            child[s:e] = a[s:e]
            idx = 0
            for i in range(size):
                while idx < size and any(b[idx][0] == x[0] for x in child if x): idx += 1
                if child[i] is None and idx < size: child[i] = b[idx]; idx += 1
            return Schedule(child)
        c1, c2 = make_child(p1.assignments, p2.assignments), make_child(p2.assignments, p1.assignments)
        c1.fitness, c2.fitness = self.fitness(c1), self.fitness(c2)
        return c1, c2

    def mutate(self, sched: Schedule):
        if random.random() > self.mutation_rate:
            return sched
        m = Schedule(sched.assignments.copy())
        i = random.randint(0, len(m.assignments) - 1)
        matkul = self.matkul_df.iloc[m.assignments[i][0]]
        slot = self._get_valid_slots(matkul, set())
        if slot:
            h, s, r = random.choice(slot)
            m.assignments[i] = (m.assignments[i][0], h, s, r)
            m.fitness = self.fitness(m)
        return m

    def to_dataframe(self, sched: Schedule) -> pd.DataFrame:
        rows = []
        for idx, h, s, r in sched.assignments:
            m = self.matkul_df.iloc[idx]
            rows.append({
                "hari": h, "sesi": s,
                "kode_matkul": m['kode_matkul'],
                "nama_matkul": m['nama_matkul'],
                "kelas": m['kelas'],
                "dosen": m['dosen'],
                "ruangan": r,
                "fitness_score": sched.fitness
            })
        return pd.DataFrame(rows)

def jadwalkan_ai(matkul, dosen, kelas, ruangan):
    ai = AIScheduler(matkul, dosen, kelas, ruangan)
    best = ai.evolve()
    return ai.to_dataframe(best)
