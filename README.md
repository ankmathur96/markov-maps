# markov-maps
Modeling maps as Markov chains to find road segments that are choke points
To see a more specific version of this, see `report.pdf`
## Introduction

### Motivation
In America, there are few things that are so universally experienced and hated as waiting in traffic. Frequently, the first to be blamed by displeased people are city planners, who are responsible for designing and improving the quality of a city’s roads. Designing an optimal road network is, in fact, a nontrivial problem to solve.

There are a variety of factors that play into how congestion develops within the road network of a city. Among these are factors like where residential areas are, where businesses are located, the geography of the region, and, most importantly, the resource contraints on being able to build roads. Working under a constrained world, it is not possible to improve infrastructure in every single location in a road network. Instead, city planners face the difficult choice of being able to improve a small set of roads with the hope of being able to improve traffic flow in a large area.

We see this, fundamentally, as a problem of ranking. Areas of the map should be ranked in terms of how badly they are over capacity. For this, we need a model that assumes facts about how traffic flows (where are businesses, where are highways, etc.) and has a sense of the capacities of roads. Using these two central components, we can simulate a map network and then rank which roads are the worst off when it comes to the ratio of capacity over expected traffic. We call a model with reasonable understanding about traffic flows and capacities a valid traffic model.

### Using Pagerank

We contend and prove that modeling the traffic in a road network with Pagerank is a valid way to analyze how traffic would flow in a network, assuming that the Markov’s chain’s probabilities are computed using an intelligent approach to assigning probabilities such that we can create a valid traffic model.

The canonical example of Pagerank involves moving to different websites with even probabilities, with websites that are visited more being ranked higher. However, more advanced Pagerank approaches frequently use more complex methods for assigning what the actual probabilities are, rather than simply evenly distributing probabilities across the different connected websites. All of these approaches still create valid Markov chains.

In order to generate what we think is a valid traffic model, we used a variety of metrics and datasets that are described in more detail in the paper.

Our final Pagerank implementation implements a crawler that crawls along the graph. It keeps track of the number of occurrences of a given node and randomly restarts after some interval, which we tuned to get different kinds of interesting data. By running this for a million iterations and by recording the number of hits for a specific node and comparing that with the capacities that we determined for a specific node, we are also able to determine which nodes are over capacity.

Therefore, what the code returns is a map with areas that are heatmapped with traffic vs. capacity. In other words, a node will only be red if the traffic that goes through that node exceeds the capacity of that node. We also return a ranking of the nodes that are most over capacity.

## Code
`python2 markov_map.py` will run our code for you, generate a matplotlib plot, and return the top graphed nodes. The dataset we obtained was for the whole Bay Area, so if you want to change the scope or the number of iterations, that can also be changed in that file.

## Results
![Generated Map](https://raw.githubusercontent.com/ankmathur96/markov-maps/master/report/figs/f1.png "Generated Map")

That is the generated map from our model, using an actual graph generated from the San Francisco Bay Area (we got the graph from “On Trip Planning Queries in Spatial Databases” (Li, Cheng, Hadjieleftheriou, Kollios, Teng 2005))
Nodes that have a brighter color have more traffic. Here's an example of the Golden Gate Bridge, notorious for having pretty bad traffic during peak time.
![Golden Gate Bridge](https://raw.githubusercontent.com/ankmathur96/markov-maps/master/report/figs/f2.png "Golden Gate Bridge")

The Embarcadero area of San Francisco, also having highly concentrated traffic nodes:

![Embarcadero](https://raw.githubusercontent.com/ankmathur96/markov-maps/master/report/figs/f3.png "Embarcadero")

Finally, we see where the top 3 nodes ranked on an actual Google Maps traffic map at commute time on Mondays at 8AM:

![Top 3 Nodes](https://raw.githubusercontent.com/ankmathur96/markov-maps/master/report/figs/fkey.jpg "Google Maps")
