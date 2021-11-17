async function postRequest(url,data){
   const res = await fetch(url, {
      method: "POST",
      headers: {
         'Content-Type': 'application/json'
         // 'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: JSON.stringify(data) // body data type must match "Content-Type" header
   });
   let respdata;
   console.log(res.headers)
   if (res.headers.get('Content-Type')=='application/json'){
      respdata = await res.json()
   }
   if (res.status==404){
      toastr.error(respdata && respdata['err'],"Network Error "+res.status )
   }
   else if (res.status!=200){
      toastr.error(respdata['err'],"Network Error "+res.status)
   }
   return respdata
}

async function getRequest(url){
   const res = await fetch(url, {
      method: "GET",
   });
   if (res.status!=200){
      toastr.error("Network Error "+res.status)
   }
   return res
}