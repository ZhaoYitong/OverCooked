import random
from deap import base
from deap import creator
from deap import tools
from foreground.models import Detail
from foreground.models import Order
from .models import Capacity
from .models import Station


class GA:
    NGEN = 200
    CXPB = 0.3
    MUTPB = 0.2
    random.seed(64)

    def __init__(self):
        self.details = Detail.objects.filter(state='未分配').order_by('order_id')
        self._n = len(self.details)
        self.aeq = []
        for detail in self.details:
            caps = Capacity.objects.filter(food_id=detail.food_id)
            self.aeq.append(tuple([cap.station_id for cap in caps]))

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.initCustom, creator.Individual, self.aeq)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", self.cxCustom)
        self.toolbox.register("mutate", self.mutCustom, aeq=self.aeq, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox.register("evaluate", self.evaluateInd)

        self.pop = self.toolbox.population(n=100)
        self.e = []  # 暂不考虑不同工位对同一菜品加工时间的不同
        self.t1 = []
        self.t2 = []
        for i in range(self._n):
            tt = int(Order.objects.get(id=self.details[i].order_id).date.timestamp())
            self.t1.append(tt)
            self.t2.append(int(Capacity.objects.filter(food_id=self.details[i].food_id)[0].time*60))
            temp_foods = [d.food_id for d in self.details.filter(order_id=self.details[i].order_id)]
            tn = max([int(Capacity.objects.filter(food_id=food)[0].time*60) for food in temp_foods])
            self.e.append(tt + tn)
        fitness = list(map(self.toolbox.evaluate, self.pop))
        for ind, fit in zip(self.pop, fitness):
            ind.fitness.values = fit
        self.fits = [ind.fitness.values[0] for ind in self.pop]
        self.best_ind = None

    def evaluateInd(self, individual):
        F = [0] * self._n
        for i in range(self._n):
            F[i] = max(max([F[j] for j, x in enumerate(individual) if x == individual[i]]), self.t1[i]) + self.t2[i]
        return sum([F[i] - self.e[i] for i in range(self._n) if F[i] > self.e[i]]),

    def initCustom(self, container, aeq):
        return container(aeq[i][random.randint(0, len(aeq[i]) - 1)] for i in range(len(aeq)))

    def cxCustom(self, ind1, ind2):
        size = min(len(ind1), len(ind2))
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size - 1)
        if cxpoint2 >= cxpoint1:
            cxpoint2 += 1
        else:
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1
        ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] = ind2[cxpoint1:cxpoint2], ind1[cxpoint1:cxpoint2]
        return ind1, ind2

    def mutCustom(self, individual, aeq, indpb):
        for i in range(len(aeq)):
            if random.random() < indpb:
                individual[i] = aeq[i][random.randint(0, len(aeq[i]) - 1)]
        return individual,

    def calculate(self):
        if self._n < 3:
            self.best_ind = tools.selBest(self.pop, k=1)[0]
            return
        g = 0
        while g < 100:
            g += 1
            offspring = self.toolbox.select(self.pop, len(self.pop))
            offspring = list(map(self.toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1:2]):
                if random.random() < GA.CXPB:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < GA.MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitness = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitness):
                ind.fitness.values = fit

            self.pop[:] = offspring
            self.fits = [ind.fitness.values[0] for ind in self.pop]
            # print("%s: %s" % (g, min(self.fits)))

        self.best_ind = tools.selBest(self.pop, k=1)[0]
        print("Best individual is %s, %s" % (self.best_ind, self.best_ind.fitness.values))

    def save(self):
        for i in range(self._n):
            self.details[i].station_id = self.best_ind[i]
            self.details[i].save()

        # 各工位前两个订单菜品置为已分配
        for stat in Station.objects.all():
            detail_qs = Detail.objects.filter(station_id=stat.id, state__in=['已分配', '未分配']).order_by('order_id')
            for i, detail in enumerate(detail_qs):
                if i < 2:
                    detail.state = '已分配'
                    detail.save()

