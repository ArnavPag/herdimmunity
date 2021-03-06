import random, sys
from person import Person
from logger import Logger
from virus import Virus

class Simulation(object):

    def __init__(self, virus, pop_size, percentage_vaccinated, initial_infected=1, avg_interactions=100):

        self.virus = virus 
        self.pop_size = pop_size
        self.percentage_vaccinated = percentage_vaccinated
        self.initial_infected = initial_infected 
        self.avg_interactions = avg_interactions
        self.population = [] 
        self.next_person_id = 0 
        self.current_infected = [] 
        self.total_infected = 0
        self.total_immune = 0 
        self.newly_dead = 0
        self.total_dead = 0 
#----------------------------------------
        self.file_name = "{}_simulation.txt".format(virus.virus_name)
        logger = Logger(self.file_name) 
        self.logger = logger
        logger.write_metadata(self.virus.virus_name, self.virus.repro_rate, self.virus.mortality_rate, self.pop_size, self.percentage_vaccinated, self.initial_infected)
#----------------------------------------
        self.herd_immunity = 1 - 1/(10*self.virus.repro_rate/(1 - self.virus.mortality_rate)) 
        self.conclusion = None 
        self.newly_infected = []
#----------------------------------------
        self._create_population()
        for person in self.current_infected:
            print(f'infected person: {person._id}')

    def _create_population(self):

        person_id = 1
        while person_id < (self.pop_size + 1) :
            while person_id < (self.initial_infected + 1):
                person = Person(person_id, False, self.virus)
                self.population.append(person)
                self.current_infected.append(person)
                self.total_infected += 1
                person_id += 1
            is_vaccinated = ((random.random() < self.percentage_vaccinated))
            person = Person(person_id, is_vaccinated)
            self.population.append(person)
            person_id += 1
            if person.is_vaccinated:
                self.total_immune += 1 
        return self.population

    def _simulation_should_continue(self):
        
        if self.total_immune >= (self.herd_immunity* len(self.population)):
            print('HERD IMMUNITY ACHIEVED')
            self.conclusion = 'herd immunity'
            self.logger.Final_data(self.conclusion, self.total_dead, len(self.population), self.total_immune)
            return False
        elif len(self.current_infected) == 0:
            print('NO MORE INFECTIONS')
            self.conclusion = 'no infections'
            self.logger.Final_data(self.conclusion, self.total_dead, len(self.population), self.total_immune)
            return False
        elif len(self.population) == 0:
            self.logger.Final_data('EVERYONE DEAD', self.total_dead, len(self.population), self.total_immune)
        else:
            return True


    def run(self):
    
        step_num = 1
        while self._simulation_should_continue() == True:
            print(f'----------TIME STEP {step_num}-----------')
            self.time_step()
            self.current_infected = []
            self._infect_newly_infected()
            self.logger.log_time_step(step_num, len(self.newly_infected), self.newly_dead, self.total_infected, self.total_dead, self.total_immune, len(self.population), self.herd_immunity)
            self.newly_infected = []
            self.newly_dead = 0
            step_num += 1
            print(f'Population Size: {len(self.population)}')


    def time_step(self):

        print(self.current_infected)
        for person in self.current_infected:
            print(f'Infected: {person._id}')
            random_people = random.sample(self.population, self.avg_interactions)
            for random_person in random_people:
                self.interaction(person, random_person)
            

    def interaction(self, person, random_person):

        print(f'{person._id} Interacted with {random_person._id}')
        assert person.is_alive == True
        assert random_person.is_alive == True

        if random_person.is_vaccinated:
            self.logger.log_interaction(person, random_person)
        elif random_person.natural_immunity:
            self.logger.log_interaction(person, random_person)
        elif random_person.virus != None:
            self.logger.log_interaction(person, random_person)
        elif random_person.is_vaccinated == False and random_person.natural_immunity == False:
            bad_luck = random.random()
            if bad_luck < self.virus.repro_rate:
               
                if any(x._id == random_person._id for x in self.newly_infected) == False:
                    print(f'{random_person._id} Caught the Virus')
                    self.logger.log_interaction(person, random_person, True)
                    self.total_infected += 1
                    self.newly_infected.append(random_person)
                else:
                    print('Clone')
            else:
                self.logger.log_interaction(person,random_person)



    def _infect_newly_infected(self):

        for sick_person in self.newly_infected:
            sick_person.virus = self.virus
            if sick_person.did_survive_infection():
                print(f'{sick_person._id} is Infected.')
                self.logger.log_infection_survival(sick_person)
                self.current_infected.append(sick_person)
                self.total_immune += 1
                
            else:
                self.logger.log_infection_survival(sick_person, True)
                self.population.remove(sick_person)
                self.newly_dead += 1
                self.total_dead += 1
                print(f'{sick_person._id} Died')              
