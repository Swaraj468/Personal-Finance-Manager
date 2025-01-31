document.addEventListener("DOMContentLoaded", function(){
    // const homepageForm = document.querySelector("#homepageForm");
    // if(homepageForm){
    //     homepageForm.addEventListener('submit', function(event){
    //         let description = document.getElementById('description').value;
    //         let amount = document.getElementById('amount').value;
            
    //         if(!description || !amount){
    //             alert('All fields are required');
    //         }else if(isNaN(amount) || amount<=0){
    //             alert('Amount must be positive');
    //             event.preventDefault()
    //         }
    //     })
    // }
    const budgetForm = document.querySelector("#budgetForm");
    if(budgetForm){
        budgetForm.addEventListener('submit', function(event){
            let category = document.getElementById('category').value;
            let budget_amount = document.getElementById('budget_amount').value;
            let start_date = document.getElementById('start_date').value;
            let end_date = document.getElementById('end_date').value;

            if(!category || !budget_amount || !start_date || !end_date){
                alert('All fields are required');
                event.preventDefault();
            }else if(isNaN(budget_amount || budget_amount <= 0)) {
                alert('Budget amount must be positive');
                event.preventDefault();
            }
        });
    }
});