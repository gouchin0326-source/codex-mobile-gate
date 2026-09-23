(function(root){
  "use strict";
  const starts={side:[[318,302],[350,302]],vertical:[[190,140],[290,205]],isometric:[[300,265],[325,340]]};
  function enemyAt(view,index,wave){const [x,y]=starts[view][index%2];return {x,y,hp:2+Math.floor((wave-1)/2),maxHp:2+Math.floor((wave-1)/2),lastHitId:-1,nextAttackAt:0,lungeUntil:0,stunUntil:0,hurtUntil:0}}
  function create(view){return {view,hp:5,maxHp:5,score:0,wave:1,enemies:[enemyAt(view,0,1)],invincibleUntil:0,respawnAt:0,recoverAt:0,lastEvent:"敵を倒して動作を検証",eventUntil:0}}
  function reset(model,view){Object.assign(model,create(view));return model}
  function stickLevel(magnitude){return magnitude<.2?"停止":magnitude<.48?"そっと":magnitude<.82?"歩行":"強く"}
  function dashTilt(previous,current,elapsedMs){return previous<.55&&current>.82&&elapsedMs>0&&elapsedMs<150}
  function step(model,cat,dt,now){
    if(model.hp<=0){if(now>=model.recoverAt){model.hp=model.maxHp;model.invincibleUntil=now+1000;model.lastEvent="復帰";model.eventUntil=now+700}return model}
    const attack=cat.attackId>0&&now<cat.attackUntil,rolling=cat.action==="roll",rollStrike=rolling&&now<cat.rollStrikeUntil;
    for(const enemy of model.enemies){
      if(enemy.hp<=0)continue;
      let dx=cat.x-enemy.x,dy=cat.y-enemy.y;if(model.view==="side")dy=0;
      let distance=Math.hypot(dx,dy),ux=distance?dx/distance:0,uy=distance?dy/distance:0;
      if(now>=enemy.stunUntil&&distance>31){const speed=Math.min(75,29+model.wave*5);enemy.x+=ux*speed*dt;enemy.y+=uy*speed*dt;if(model.view==="side")enemy.y=302}
      dx=enemy.x-cat.x;dy=model.view==="side"?0:enemy.y-cat.y;distance=Math.hypot(dx,dy);
      const forward=dx*cat.dirX+dy*cat.dirY;
      if((attack||rollStrike)&&enemy.lastHitId!==cat.attackId&&distance<(cat.action==="dashAttack"?88:cat.action==="kick"?78:rollStrike?62:65)&&forward>-22){const damage=cat.action==="kick"||cat.action==="dashAttack"?2:1;enemy.hp=Math.max(0,enemy.hp-damage);enemy.lastHitId=cat.attackId;enemy.stunUntil=now+230;enemy.hurtUntil=now+180;enemy.x=Math.max(45,Math.min(345,enemy.x+(distance?dx/distance:cat.dirX)*15));enemy.y=Math.max(95,Math.min(375,enemy.y+(distance?dy/distance:cat.dirY)*8));model.lastEvent=enemy.hp?"命中！":"撃破！";model.eventUntil=now+450;if(!enemy.hp)model.score++}
      if(enemy.hp>0&&distance<30&&now>enemy.nextAttackAt){enemy.nextAttackAt=now+850;enemy.lungeUntil=now+170;if(!rolling&&!cat.invincible&&now>=model.invincibleUntil){model.hp--;model.invincibleUntil=now+900;model.lastEvent=model.hp?"被弾！":"体力0・まもなく復帰";model.eventUntil=now+600;if(!model.hp)model.recoverAt=now+1200}else if(rolling||cat.invincible){model.lastEvent=rolling?"ローリング回避":"ジャンプ・ダッシュ回避";model.eventUntil=now+400}}
    }
    if(model.enemies.every(enemy=>enemy.hp<=0)){if(!model.respawnAt)model.respawnAt=now+650;if(now>=model.respawnAt){model.wave++;model.enemies=Array.from({length:Math.min(2,model.wave)},(_,index)=>enemyAt(model.view,index,model.wave));model.respawnAt=0;model.lastEvent=`第${model.wave}波`;model.eventUntil=now+600}}
    return model
  }
  root.HoshiCatCombat=Object.freeze({create,reset,step,stickLevel,dashTilt});
})(window);
