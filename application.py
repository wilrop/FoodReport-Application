from SPARQLWrapper import SPARQLWrapper, JSON


# The procedure that will run the application.
def run_application():
    print("Generating a food report for spaghetti bolognese")
    print("----------------------------------------------------------")
    sparql = SPARQLWrapper("http://localhost:8080/fuseki/foodreport/sparql")  # SPARQL server
    sparql.setReturnFormat(JSON)  # Return format

    # This query will get all the ingredients in the ontology.
    query1 = """
    PREFIX ontology: <http://www.foodreport.be/ontology#>
    PREFIX data: <http://www.foodreport.be/data#>

    SELECT ?ingredient ?name
    WHERE {
    data:Spaghetti%20Bolognese ontology:needsIngredient ?ingredient .
    ?ingredient ontology:ingredientName ?name
    }
    
    """

    sparql.setQuery(query1)
    results1 = sparql.query().convert()

    ingredient_lst = results1["results"]["bindings"]
    ingredient_uris = [ingredient["ingredient"]["value"] for ingredient in ingredient_lst]
    ingredient_names = [ingredient["name"]["value"] for ingredient in ingredient_lst]
    print("For this recipe you need the following ingredients: ")
    for idx, ingredient in enumerate(ingredient_names):
        print(str(idx + 1) + ". " + ingredient)

    print("")  # An ugly fix for a empty line.

    # This query will get all of the steps for the recipe.
    query2 = """
    PREFIX ontology: <http://www.foodreport.be/ontology#>
    PREFIX data: <http://www.foodreport.be/data#>

    SELECT ?step ?description
    WHERE {
    ?step ontology:describesRecipe data:Spaghetti%20Bolognese .
    ?step ontology:description ?description
    } ORDER BY ASC(?step)
    
    """
    sparql.setQuery(query2)
    results2 = sparql.query().convert()
    step_lst = results2["results"]["bindings"]
    step_descriptions = [step["description"]["value"] for step in step_lst]

    print("There are " + str(len(step_descriptions)) + " steps to complete this recipe:")
    for idx, description in enumerate(step_descriptions):
        print(str(idx + 1) + ". " + description)

    print("")

    # This query will get all the nutrition values for the entire recipe.
    query3 = """
    PREFIX ontology: <http://www.foodreport.be/ontology#>
    PREFIX data: <http://www.foodreport.be/data#>

    SELECT (SUM(?sugar) AS ?totalSugar) (SUM(?proteins) AS ?totalProteins) (SUM(?sodium) AS ?totalSodium) (SUM(?fat) AS ?totalFat) (SUM(?calories) AS ?totalCalories) (SUM(?calcium) AS ?totalCalcium) (SUM(?carbohydrates) AS ?totalCarbohydrates)
    WHERE {
    data:Spaghetti%20Bolognese ontology:needsIngredient ?ingredient .
    ?ingredient ontology:sugar ?sugar .
    ?ingredient ontology:proteins ?proteins .
    ?ingredient ontology:sodium ?sodium .
    ?ingredient ontology:fat ?fat .
    ?ingredient ontology:calories ?calories .
    ?ingredient ontology:calcium ?calcium .
    ?ingredient ontology:carbohydrates ?carbohydrates
    }
    """
    sparql.setQuery(query3)
    results3 = sparql.query().convert()
    nutrition_values = results3["results"]["bindings"][0]

    print("The recipe has the following nutrition values (in grams or milliliters if it is present in a liquid):")
    print("• Sugar: " + nutrition_values["totalSugar"]["value"])
    print("• Proteins: " + nutrition_values["totalProteins"]["value"])
    print("• Sodium: " + nutrition_values["totalSodium"]["value"])
    print("• Fat: " + nutrition_values["totalFat"]["value"])
    print("• Calories: " + nutrition_values["totalCalories"]["value"])
    print("• Calcium: " + nutrition_values["totalCalcium"]["value"])
    print("• Carbohydrates: " + nutrition_values["totalCarbohydrates"]["value"])

    print("")

    for idx, ingredient in enumerate(ingredient_uris):
        # Parse the ingredient to the correct format
        ingredient = ingredient.split("/")[-1]
        ingredient = ingredient.replace("#", ":")

        # This query will get the ethical scores for a particular ingredient for a user from Italy.
        query4 = """
        PREFIX ontology: <http://www.foodreport.be/ontology#>
        PREFIX data: <http://www.foodreport.be/data#>

        SELECT ?countryName (AVG(?labourScore) AS ?averageLabourScore) (AVG(?environmentScore) AS ?averageEnvironmentScore) (AVG(?trajectoryScore) AS ?avgTrajectoryScore)
        WHERE {
        """ + ingredient + """ ontology:manufacturedFrom ?country .
        ?country ontology:countryName ?countryName .
        ?country ontology:imposes ?law .
        ?law ontology:appliesToFoodType ?foodtype .
        """ + ingredient + """ ontology:hasFoodType ?foodtype .
        ?law ontology:labourScore ?labourScore .
        ?law ontology:environmentScore ?environmentScore .
  
        ?trajectory ontology:trajectoryFrom ?country .
        ?trajectory ontology:trajectoryTo data:Italy .
        ?trajectory ontology:ships """ + ingredient + """ .
        ?trajectory ontology:trajectoryScore ?trajectoryScore
  
        } GROUP BY ?countryName       
        """

        sparql.setQuery(query4)
        results4 = sparql.query().convert()
        countries = results4["results"]["bindings"]
        print("The " + ingredient_names[idx] + " can be sourced from " + str(len(countries)) + " countries with the following scores:")
        print("For all scores, higher is better")
        for country in countries:
            print("- From " + country["countryName"]["value"])
            print("• Average labour score: " + country["averageLabourScore"]["value"])
            print("• Average environment score: " + country["averageEnvironmentScore"]["value"])
            print("• Average trajectory score: " + country["avgTrajectoryScore"]["value"])
            print("")


if __name__ == "__main__":
    run_application()
