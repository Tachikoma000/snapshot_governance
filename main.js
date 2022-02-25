/* Moralis init code */
const serverUrl = "https://qc88ykdhlj8a.usemoralis.com:2053/server";
const appId = "wcsKMiU8Y9lXyZ4S0Cxynuv7LBWRF0akqsE8yiEj";
Moralis.start({ serverUrl, appId });

/* Authentication code */
async function login() {
  let user = Moralis.User.current();
  if (!user) {
    user = await Moralis.authenticate({ signingMessage: "Log in using Moralis" })
      .then(function (user) {
        console.log("logged in user:", user);
        console.log(user.get("ethAddress"));
      })
      .catch(function (error) {
        console.log(error);
      });
  }
}

async function logOut() {
  await Moralis.User.logOut();
  console.log("logged out");
}

document.getElementById("log_in").onclick = login;
document.getElementById("log_out").onclick = logOut;
